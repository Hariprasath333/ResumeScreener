from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class RecommendationEnum(str, Enum):
    STRONG_MATCH = "STRONG_MATCH"
    MATCH = "MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    WEAK_MATCH = "WEAK_MATCH"


class ScoresBreakdown(BaseModel):
    required_skills: float = Field(ge=0, le=100)
    preferred_skills: float = Field(ge=0, le=100)
    experience: float = Field(ge=0, le=100)
    education: float = Field(ge=0, le=100)
    responsibilities: float = Field(ge=0, le=100)
    semantic_match: float = Field(ge=0, le=100)


class RequirementEvidence(BaseModel):
    requirement: str
    evidence: str = ""
    source: str = "Resume"
    match_type: str = "MATCHED"  # MATCHED, MISSING, PARTIAL
    importance: str = "REQUIRED"  # REQUIRED, PREFERRED
    score: float = 100.0


from pydantic import BaseModel, Field, ConfigDict

class MatchResultResponse(BaseModel):
    id: str
    candidate_id: str
    candidate_name: str
    job_id: str
    job_title: str
    overall_score: float = Field(ge=0, le=100)
    recommendation: RecommendationEnum
    confidence: float = Field(ge=0, le=1)
    critical_requirement_missing: bool = False
    
    scores: ScoresBreakdown
    matched_requirements: List[RequirementEvidence] = Field(default_factory=list)
    missing_requirements: List[RequirementEvidence] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    critical_gaps: List[str] = Field(default_factory=list)
    explanation: str = ""
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchScreeningRequest(BaseModel):
    resume_ids: Optional[List[str]] = Field(default=None, description="Optional subset of resume IDs; screens all if null")


class CandidateRankItem(BaseModel):
    rank: int
    match_id: str
    candidate_id: str
    candidate_name: str
    resume_id: str
    overall_score: float
    fit_score_10: float = 0.0
    recommendation: RecommendationEnum
    confidence: float
    critical_requirement_missing: bool
    matched_skills_count: int
    total_required_skills: int
    experience_years: float
    explanation: Optional[str] = ""
    created_at: datetime
