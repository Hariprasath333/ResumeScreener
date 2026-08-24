from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CandidateContact(BaseModel):
    name: str = Field(default="Candidate", description="Full name of candidate")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="City / Country")
    linkedin: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    github: Optional[str] = Field(default=None, description="GitHub profile URL")


class SkillCategories(BaseModel):
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)
    devops: List[str] = Field(default_factory=list)
    ai_ml: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)

    @property
    def all_skills(self) -> List[str]:
        combined = (
            self.programming_languages +
            self.frameworks +
            self.databases +
            self.cloud +
            self.devops +
            self.ai_ml +
            self.tools
        )
        # Deduplicate preserving order
        seen = set()
        result = []
        for item in combined:
            item_lower = item.strip().lower()
            if item_lower and item_lower not in seen:
                seen.add(item_lower)
                result.append(item.strip())
        return result


class WorkExperience(BaseModel):
    company: str = ""
    role: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_months: int = 0
    responsibilities: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    degree: str = ""
    university: str = ""
    field: str = ""
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None


class ProjectEntry(BaseModel):
    name: str = ""
    description: str = ""
    technologies: List[str] = Field(default_factory=list)
    contributions: List[str] = Field(default_factory=list)


class CertificationEntry(BaseModel):
    name: str = ""
    issuer: Optional[str] = None
    date: Optional[str] = None


class StructuredResume(BaseModel):
    candidate: CandidateContact = Field(default_factory=CandidateContact)
    skills: SkillCategories = Field(default_factory=SkillCategories)
    experience: List[WorkExperience] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[CertificationEntry] = Field(default_factory=list)


class ResumeUploadResponse(BaseModel):
    id: str
    candidate_id: str
    file_name: str
    file_type: str
    parser_status: str
    ocr_used: bool
    extraction_confidence: float
    structured_data: StructuredResume
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
