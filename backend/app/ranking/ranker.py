from typing import List, Optional
from app.schemas.match import CandidateRankItem, RecommendationEnum


class CandidateRanker:
    """Ranks and filters candidate match results for a Job Description."""

    def rank_candidates(
        self,
        match_records: List[dict],
        min_score: Optional[float] = None,
        recommendation_filter: Optional[str] = None,
        require_all_mandatory: bool = False
    ) -> List[CandidateRankItem]:
        """
        Ranks match records by composite score, mandatory penalty status, and skill matches.
        """
        filtered = []

        for record in match_records:
            score = record["overall_score"]
            rec = record["recommendation"]
            crit_missing = record["critical_requirement_missing"]

            if min_score is not None and score < min_score:
                continue

            if recommendation_filter and rec != recommendation_filter:
                continue

            if require_all_mandatory and crit_missing:
                continue

            filtered.append(record)

        # Sort criteria:
        # 1. No critical requirement missing first (False < True)
        # 2. Higher overall_score
        # 3. Higher matched_skills_count
        filtered.sort(
            key=lambda r: (
                r.get("critical_requirement_missing", False),
                -r.get("overall_score", 0),
                -r.get("matched_skills_count", 0),
                -r.get("experience_years", 0)
            )
        )

        from datetime import datetime, timezone
        ranked_items = []
        for idx, item in enumerate(filtered, start=1):
            score = item["overall_score"]
            fit_10 = round(score / 10.0, 1)
            ranked_items.append(CandidateRankItem(
                rank=idx,
                match_id=item.get("match_id", f"match-{idx}"),
                candidate_id=item.get("candidate_id", f"cand-{idx}"),
                candidate_name=item.get("candidate_name", "Candidate"),
                resume_id=item.get("resume_id", f"res-{idx}"),
                overall_score=score,
                fit_score_10=fit_10,
                recommendation=item["recommendation"],
                confidence=item.get("confidence", 0.9),
                critical_requirement_missing=item.get("critical_requirement_missing", False),
                matched_skills_count=item.get("matched_skills_count", 0),
                total_required_skills=item.get("total_required_skills", 0),
                experience_years=item.get("experience_years", 0.0),
                explanation=item.get("explanation", ""),
                created_at=item.get("created_at") or datetime.now(timezone.utc)
            ))

        return ranked_items
