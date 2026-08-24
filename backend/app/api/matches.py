from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.base import Job, Resume, Candidate, MatchResult, MatchEvidence
from app.matcher.scorer import MatchScorer
from app.ranking.ranker import CandidateRanker
from app.schemas.resume import StructuredResume
from app.schemas.job import StructuredJD
from app.schemas.match import (
    BatchScreeningRequest, MatchResultResponse, CandidateRankItem,
    ScoresBreakdown, RequirementEvidence
)

router = APIRouter(prefix="/api", tags=["Screening & Matching"])

scorer = MatchScorer()
ranker = CandidateRanker()


@router.post("/jobs/{job_id}/screen")
def screen_candidates(
    job_id: str,
    request_data: Optional[BatchScreeningRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Run candidate screening engine for a Job Description across all (or specified subset of) uploaded resumes.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    jd_structured = StructuredJD.model_validate(job.structured_requirements or {})

    # Fetch Resumes
    query = db.query(Resume)
    if request_data and request_data.resume_ids:
        query = query.filter(Resume.id.in_(request_data.resume_ids))
    resumes = query.all()

    if not resumes:
        return {
            "job_id": job_id,
            "screened_count": 0,
            "message": "No resumes available for screening. Upload resumes first."
        }

    screened_results = []

    for resume in resumes:
        cand = db.query(Candidate).filter(Candidate.id == resume.candidate_id).first()
        resume_structured = StructuredResume.model_validate(resume.structured_data or {})

        # Compute Score & Evidence via Deterministic Matcher Engine
        evaluation = scorer.score_candidate(resume_structured, jd_structured)

        # Delete existing match result if screening again
        existing_match = db.query(MatchResult).filter(
            MatchResult.job_id == job_id,
            MatchResult.candidate_id == resume.candidate_id
        ).first()
        if existing_match:
            db.delete(existing_match)
            db.flush()

        # Build MatchResult DB Record
        match_rec = MatchResult(
            candidate_id=resume.candidate_id,
            job_id=job_id,
            overall_score=evaluation["overall_score"],
            recommendation=evaluation["recommendation"].value,
            confidence=evaluation["confidence"],
            critical_requirement_missing=evaluation["critical_requirement_missing"],
            scores_breakdown=evaluation["scores"].model_dump(),
            strengths=evaluation["strengths"],
            weaknesses=evaluation["weaknesses"],
            critical_gaps=evaluation["critical_gaps"],
            explanation=f"Overall score {evaluation['overall_score']}/100. " + " ".join(evaluation["strengths"]) + " " + " ".join(evaluation["critical_gaps"])
        )
        db.add(match_rec)
        db.flush()

        # Save evidences
        for ev in evaluation["matched_requirements"] + evaluation["missing_requirements"]:
            ev_record = MatchEvidence(
                match_result_id=match_rec.id,
                requirement=ev.requirement,
                evidence=ev.evidence,
                source=ev.source,
                match_type=ev.match_type,
                importance=ev.importance
            )
            db.add(ev_record)

        db.commit()
        db.refresh(match_rec)

        screened_results.append({
            "match_id": match_rec.id,
            "candidate_id": cand.id,
            "candidate_name": cand.name,
            "overall_score": match_rec.overall_score,
            "recommendation": match_rec.recommendation
        })

    return {
        "job_id": job_id,
        "job_title": job.title,
        "screened_count": len(screened_results),
        "results": screened_results
    }


@router.get("/jobs/{job_id}/candidates", response_model=List[CandidateRankItem])
def get_ranked_candidates(
    job_id: str,
    min_score: Optional[float] = Query(None, ge=0, le=100),
    recommendation: Optional[str] = Query(None),
    require_all_mandatory: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get ranked shortlist of candidates screened for a specific Job Description.
    Supports filtering by score, recommendation tier, and mandatory skill compliance.
    """
    matches = db.query(MatchResult).filter(MatchResult.job_id == job_id).all()
    if not matches:
        return []

    records = []
    for m in matches:
        cand = db.query(Candidate).filter(Candidate.id == m.candidate_id).first()
        res = db.query(Resume).filter(Resume.candidate_id == m.candidate_id).first()

        # Extract stats from structured data if available
        matched_count = 0
        total_req = 0
        exp_yrs = 0.0

        if res and res.structured_data:
            res_struct = StructuredResume.model_validate(res.structured_data)
            exp_yrs = scorer.exp_calc.calculate_total_years(res_struct.experience)

        ev_matched = db.query(MatchEvidence).filter(
            MatchEvidence.match_result_id == m.id,
            MatchEvidence.match_type == "MATCHED",
            MatchEvidence.importance == "REQUIRED"
        ).count()
        
        ev_total_req = db.query(MatchEvidence).filter(
            MatchEvidence.match_result_id == m.id,
            MatchEvidence.importance == "REQUIRED"
        ).count()

        records.append({
            "match_id": m.id,
            "candidate_id": m.candidate_id,
            "candidate_name": cand.name if cand else "Candidate",
            "resume_id": res.id if res else "",
            "overall_score": m.overall_score,
            "recommendation": m.recommendation,
            "confidence": m.confidence,
            "critical_requirement_missing": m.critical_requirement_missing,
            "matched_skills_count": ev_matched,
            "total_required_skills": max(ev_total_req, 1),
            "experience_years": exp_yrs,
            "explanation": m.explanation or "",
            "created_at": m.created_at
        })

    return ranker.rank_candidates(
        records,
        min_score=min_score,
        recommendation_filter=recommendation,
        require_all_mandatory=require_all_mandatory
    )


@router.get("/matches/{match_id}", response_model=MatchResultResponse)
def get_match_detail(match_id: str, db: Session = Depends(get_db)):
    """
    Get detailed match evaluation including radar score breakdown, exact quoted evidence, missing requirements, and recommendations.
    """
    match = db.query(MatchResult).filter(MatchResult.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match result not found")

    cand = db.query(Candidate).filter(Candidate.id == match.candidate_id).first()
    job = db.query(Job).filter(Job.id == match.job_id).first()

    evidences = db.query(MatchEvidence).filter(MatchEvidence.match_result_id == match_id).all()

    matched_reqs = []
    missing_reqs = []

    for ev in evidences:
        item = RequirementEvidence(
            requirement=ev.requirement,
            evidence=ev.evidence or "",
            source=ev.source or "Resume",
            match_type=ev.match_type,
            importance=ev.importance,
            score=100.0 if ev.match_type == "MATCHED" else 0.0
        )
        if ev.match_type == "MATCHED":
            matched_reqs.append(item)
        else:
            missing_reqs.append(item)

    scores_obj = ScoresBreakdown.model_validate(match.scores_breakdown)

    return MatchResultResponse(
        id=match.id,
        candidate_id=match.candidate_id,
        candidate_name=cand.name if cand else "Candidate",
        job_id=match.job_id,
        job_title=job.title if job else "Job Position",
        overall_score=match.overall_score,
        recommendation=match.recommendation,
        confidence=match.confidence,
        critical_requirement_missing=match.critical_requirement_missing,
        scores=scores_obj,
        matched_requirements=matched_reqs,
        missing_requirements=missing_reqs,
        strengths=match.strengths or [],
        weaknesses=match.weaknesses or [],
        critical_gaps=match.critical_gaps or [],
        explanation=match.explanation or "",
        created_at=match.created_at
    )
