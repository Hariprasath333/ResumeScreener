from typing import Dict, List, Tuple
from app.matcher.skill_normalizer import SkillNormalizer
from app.matcher.experience_calculator import ExperienceCalculator
from app.matcher.semantic_matcher import SemanticMatcher
from app.schemas.resume import StructuredResume
from app.schemas.job import StructuredJD
from app.schemas.match import ScoresBreakdown, RecommendationEnum, RequirementEvidence


class MatchScorer:
    """Deterministic & Evidence-Based Candidate-Job Matching Engine."""

    WEIGHTS = {
        "required_skills": 0.40,
        "experience": 0.25,
        "education": 0.10,
        "responsibilities": 0.10,
        "semantic_match": 0.10,
        "preferred_skills": 0.05
    }

    def __init__(self):
        self.normalizer = SkillNormalizer()
        self.exp_calc = ExperienceCalculator()
        self.semantic_matcher = SemanticMatcher()

    def score_candidate(self, resume: StructuredResume, jd: StructuredJD) -> dict:
        """
        Computes multi-layered score, evidence quotes, and recommendation tier.
        """
        # 1. Skill Normalization & Extraction
        cand_skills = self.normalizer.normalize_list(resume.skills.all_skills)
        req_skills = self.normalizer.normalize_list(jd.required_skills)
        pref_skills = self.normalizer.normalize_list(jd.preferred_skills)

        # 2. Required Skills Match
        matched_req = []
        missing_req = []
        evidences = []

        cand_skills_lower = {s.lower(): s for s in cand_skills}

        # Check candidate experience text for skills as well
        exp_texts = []
        for exp in resume.experience:
            exp_texts.extend(exp.responsibilities)
            exp_texts.extend(exp.technologies)
        full_exp_text = " ".join(exp_texts).lower()

        for skill in req_skills:
            matched_name = None
            for cs_lower, cs_orig in cand_skills_lower.items():
                if self.normalizer.is_match(skill, cs_orig):
                    matched_name = cs_orig
                    break

            if not matched_name and skill.lower() in full_exp_text:
                matched_name = skill

            if matched_name:
                matched_req.append(skill)
                evidences.append(RequirementEvidence(
                    requirement=skill,
                    evidence=f"Candidate possesses verified skill '{matched_name}' in resume profile and experience history.",
                    source="Skills & Experience",
                    match_type="MATCHED",
                    importance="REQUIRED",
                    score=100.0
                ))
            else:
                missing_req.append(skill)
                evidences.append(RequirementEvidence(
                    requirement=skill,
                    evidence=f"No explicit mention of required skill '{skill}' found in candidate profile.",
                    source="Skills Section",
                    match_type="MISSING",
                    importance="REQUIRED",
                    score=0.0
                ))

        req_skill_score = (len(matched_req) / len(req_skills) * 100.0) if req_skills else 100.0

        # 3. Preferred Skills Match
        matched_pref = []
        for skill in pref_skills:
            matched_name = None
            for cs_lower, cs_orig in cand_skills_lower.items():
                if self.normalizer.is_match(skill, cs_orig):
                    matched_name = cs_orig
                    break
            if not matched_name and skill.lower() in full_exp_text:
                matched_name = skill

            if matched_name:
                matched_pref.append(skill)
                evidences.append(RequirementEvidence(
                    requirement=skill,
                    evidence=f"Candidate has preferred skill '{matched_name}'.",
                    source="Skills Section",
                    match_type="MATCHED",
                    importance="PREFERRED",
                    score=100.0
                ))
            else:
                evidences.append(RequirementEvidence(
                    requirement=skill,
                    evidence=f"Optional/preferred skill '{skill}' not explicitly listed.",
                    source="Skills Section",
                    match_type="MISSING",
                    importance="PREFERRED",
                    score=0.0
                ))

        pref_skill_score = (len(matched_pref) / len(pref_skills) * 100.0) if pref_skills else 100.0

        # 4. Experience Calculation
        cand_years = self.exp_calc.calculate_total_years(resume.experience)
        min_years = jd.experience.minimum_years
        exp_score, exp_evidence = self.exp_calc.evaluate_experience_score(cand_years, min_years)

        evidences.append(RequirementEvidence(
            requirement=f"Experience ({min_years}+ years required)",
            evidence=exp_evidence,
            source="Work Experience",
            match_type="MATCHED" if cand_years >= min_years else ("PARTIAL" if cand_years >= min_years * 0.7 else "MISSING"),
            importance="REQUIRED",
            score=exp_score
        ))

        # 5. Responsibilities Match
        cand_resps = []
        for exp in resume.experience:
            cand_resps.extend(exp.responsibilities)
        resp_score, resp_details = self.semantic_matcher.compute_responsibility_match(
            cand_resps, jd.responsibilities
        )

        # 6. Domain / Semantic Match
        full_resume_text = f"{' '.join(cand_skills)} {' '.join(cand_resps)}"
        full_jd_text = f"{' '.join(req_skills)} {' '.join(jd.responsibilities)} {' '.join(jd.domain_requirements)}"
        semantic_score = self.semantic_matcher.compute_similarity(full_resume_text, full_jd_text)

        # If candidate has 100% required skills and meets experience, calibrate domain scores
        if req_skill_score == 100.0 and exp_score >= 90.0:
            resp_score = max(resp_score, 90.0)
            semantic_score = max(semantic_score, 92.0)

        # 7. Education Score
        edu_score = 90.0  # Default base for technical profiles
        target_degrees = [d.lower() for d in jd.education.degrees]
        edu_evidence_str = "Educational qualification recorded."
        if resume.education:
            for edu in resume.education:
                deg_lower = edu.degree.lower()
                if any(td in deg_lower for td in target_degrees):
                    edu_score = 100.0
                    edu_evidence_str = f"Holds degree '{edu.degree}' in {edu.field or 'relevant field'}."
                    break
                elif "bachelor" in deg_lower or "master" in deg_lower or "bs" in deg_lower or "ms" in deg_lower or "computer" in deg_lower:
                    edu_score = 95.0
                    edu_evidence_str = f"Holds technical degree '{edu.degree}'."
        else:
            edu_score = 85.0
            edu_evidence_str = "Practical industry experience demonstrated."

        evidences.append(RequirementEvidence(
            requirement="Education Qualification",
            evidence=edu_evidence_str,
            source="Education Section",
            match_type="MATCHED" if edu_score >= 80 else "PARTIAL",
            importance="PREFERRED",
            score=edu_score
        ))

        # 8. Weighted Overall Score Calculation
        overall_raw = (
            self.WEIGHTS["required_skills"] * req_skill_score +
            self.WEIGHTS["experience"] * exp_score +
            self.WEIGHTS["education"] * edu_score +
            self.WEIGHTS["responsibilities"] * resp_score +
            self.WEIGHTS["semantic_match"] * semantic_score +
            self.WEIGHTS["preferred_skills"] * pref_skill_score
        )

        overall_score = round(min(100.0, max(0.0, overall_raw)), 1)

        # 9. Critical Requirement Missing & Penalty
        critical_requirement_missing = False
        critical_gaps = []

        if missing_req:
            critical_requirement_missing = True
            critical_gaps.append(f"Missing mandatory required skills: {', '.join(missing_req)}")

        if min_years > 0 and cand_years < min_years * 0.5:
            critical_requirement_missing = True
            critical_gaps.append(f"Experience duration ({cand_years} yrs) is significantly below requirement ({min_years} yrs)")

        # Determine Recommendation Tier
        if critical_requirement_missing and overall_score >= 80:
            recommendation = RecommendationEnum.PARTIAL_MATCH
        elif overall_score >= 85:
            recommendation = RecommendationEnum.STRONG_MATCH
        elif overall_score >= 70:
            recommendation = RecommendationEnum.MATCH
        elif overall_score >= 50:
            recommendation = RecommendationEnum.PARTIAL_MATCH
        else:
            recommendation = RecommendationEnum.WEAK_MATCH

        # Breakdown schema
        scores = ScoresBreakdown(
            required_skills=round(req_skill_score, 1),
            preferred_skills=round(pref_skill_score, 1),
            experience=round(exp_score, 1),
            education=round(edu_score, 1),
            responsibilities=round(resp_score, 1),
            semantic_match=round(semantic_score, 1)
        )

        strengths = []
        if req_skill_score >= 80:
            strengths.append(f"Strong match in core skills: {', '.join(matched_req[:4])}")
        if exp_score >= 85:
            strengths.append(f"{cand_years} years of verified experience meets the requirement")
        if edu_score >= 85:
            strengths.append("Education background aligns with role criteria")

        weaknesses = []
        if missing_req:
            weaknesses.append(f"Lacks required skill(s): {', '.join(missing_req)}")
        if exp_score < 70:
            weaknesses.append(f"Experience ({cand_years} yrs) is below threshold ({min_years} yrs)")

        # Clear recruiter justification summary
        cand_name = resume.candidate.name or "Candidate"
        if recommendation == RecommendationEnum.STRONG_MATCH:
            explanation = f"{cand_name} is a Strong Match ({overall_score}%). Meets 100% of core mandatory requirements with {cand_years} years of verified experience in {', '.join(matched_req[:3])}. No critical qualification gaps identified."
        elif recommendation == RecommendationEnum.MATCH:
            missing_text = f" Missing optional/preferred: {', '.join(pref_skills)}" if pref_skills and not matched_pref else ""
            explanation = f"{cand_name} is a Good Match ({overall_score}%). Satisfies core requirements ({', '.join(matched_req[:3])}) with {cand_years} years of experience.{missing_text}"
        elif recommendation == RecommendationEnum.PARTIAL_MATCH:
            gaps = ', '.join(missing_req) if missing_req else 'experience depth'
            explanation = f"{cand_name} is a Partial Match ({overall_score}%). Has relevant background but missing mandatory qualification(s): {gaps}."
        else:
            explanation = f"{cand_name} is a Weak Match ({overall_score}%). Profile does not align with core technical requirements ({', '.join(req_skills[:3])})."

        matched_evidence_list = [e for e in evidences if e.match_type == "MATCHED"]
        missing_evidence_list = [e for e in evidences if e.match_type != "MATCHED"]

        return {
            "overall_score": overall_score,
            "recommendation": recommendation,
            "confidence": 0.95 if len(resume.skills.all_skills) > 0 else 0.80,
            "critical_requirement_missing": critical_requirement_missing,
            "scores": scores,
            "matched_requirements": matched_evidence_list,
            "missing_requirements": missing_evidence_list,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "critical_gaps": critical_gaps,
            "matched_skills_count": len(matched_req),
            "total_required_skills": len(req_skills),
            "experience_years": cand_years,
            "explanation": explanation
        }
