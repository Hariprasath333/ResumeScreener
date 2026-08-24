import pytest
from app.matcher.scorer import MatchScorer
from app.schemas.resume import StructuredResume, CandidateContact, SkillCategories, WorkExperience, EducationEntry
from app.schemas.job import StructuredJD, ExperienceRequirement, EducationRequirement
from app.schemas.match import RecommendationEnum


def test_scorer_strong_match():
    scorer = MatchScorer()

    resume = StructuredResume(
        candidate=CandidateContact(name="John Doe"),
        skills=SkillCategories(programming_languages=["Java", "Python"], frameworks=["Spring Boot"], databases=["PostgreSQL"]),
        experience=[WorkExperience(company="Acme", role="Backend Dev", duration_months=36)],
        education=[EducationEntry(degree="Bachelor of Science", field="Computer Science")]
    )

    jd = StructuredJD(
        role="Java Developer",
        required_skills=["Java", "Spring Boot", "PostgreSQL"],
        preferred_skills=["Python"],
        experience=ExperienceRequirement(minimum_years=2.0),
        education=EducationRequirement(degrees=["Bachelor"], fields=["Computer Science"])
    )

    result = scorer.score_candidate(resume, jd)

    assert result["overall_score"] >= 85.0
    assert result["recommendation"] == RecommendationEnum.STRONG_MATCH
    assert result["critical_requirement_missing"] is False
    assert result["matched_skills_count"] == 3


def test_scorer_missing_critical_requirement_penalty():
    scorer = MatchScorer()

    # Candidate missing mandatory skill "Kafka"
    resume = StructuredResume(
        candidate=CandidateContact(name="Jane Smith"),
        skills=SkillCategories(programming_languages=["Java"], frameworks=["Spring Boot"]),
        experience=[WorkExperience(company="Beta", role="Dev", duration_months=36)],
        education=[EducationEntry(degree="Bachelor", field="Computer Science")]
    )

    jd = StructuredJD(
        role="Streaming Backend Engineer",
        required_skills=["Java", "Kafka"],  # Candidate lacks Kafka
        experience=ExperienceRequirement(minimum_years=2.0)
    )

    result = scorer.score_candidate(resume, jd)

    assert result["critical_requirement_missing"] is True
    assert "Kafka" in result["critical_gaps"][0]
    # Check recommendation is NOT Strong Match due to missing critical requirement
    assert result["recommendation"] in [RecommendationEnum.PARTIAL_MATCH, RecommendationEnum.MATCH, RecommendationEnum.WEAK_MATCH]
