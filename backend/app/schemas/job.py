from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ExperienceRequirement(BaseModel):
    minimum_years: float = Field(default=0.0, description="Minimum required years of experience")
    preferred_years: Optional[float] = Field(default=None, description="Preferred years of experience")


class EducationRequirement(BaseModel):
    degrees: List[str] = Field(default_factory=list, description="Target degrees, e.g. Bachelor, Master")
    fields: List[str] = Field(default_factory=list, description="Fields of study, e.g. Computer Science")


class StructuredJD(BaseModel):
    role: str = Field(default="Software Engineer", description="Job title or role")
    seniority: str = Field(default="mid", description="Seniority level: entry, mid, senior, lead")
    required_skills: List[str] = Field(default_factory=list, description="Mandatory required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Optional preferred skills")
    experience: ExperienceRequirement = Field(default_factory=ExperienceRequirement)
    education: EducationRequirement = Field(default_factory=EducationRequirement)
    responsibilities: List[str] = Field(default_factory=list)
    domain_requirements: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


class JobCreate(BaseModel):
    title: str
    company: Optional[str] = "TechCorp"
    description: str


from pydantic import BaseModel, Field, ConfigDict

class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    description: str
    structured_requirements: StructuredJD
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
