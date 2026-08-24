import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base


def generate_uuid():
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    github = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    # Relationships
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    matches = relationship("MatchResult", back_populates="candidate", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=generate_uuid)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)
    parser_status = Column(String, default="SUCCESS")  # SUCCESS, FAILED, PARALLEL_PARSED
    ocr_used = Column(Boolean, default=False)
    extraction_confidence = Column(Float, default=1.0)
    structured_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=True, default="TechCorp")
    description = Column(Text, nullable=False)
    structured_requirements = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    # Relationships
    matches = relationship("MatchResult", back_populates="job", cascade="all, delete-orphan")


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    overall_score = Column(Float, nullable=False, index=True)
    recommendation = Column(String, nullable=False)  # STRONG_MATCH, MATCH, PARTIAL_MATCH, WEAK_MATCH
    confidence = Column(Float, default=0.9)
    critical_requirement_missing = Column(Boolean, default=False)
    
    scores_breakdown = Column(JSON, nullable=False)  # {required_skills, preferred_skills, experience, ...}
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    critical_gaps = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    # Relationships
    candidate = relationship("Candidate", back_populates="matches")
    job = relationship("Job", back_populates="matches")
    evidences = relationship("MatchEvidence", back_populates="match_result", cascade="all, delete-orphan")


class MatchEvidence(Base):
    __tablename__ = "match_evidences"

    id = Column(String, primary_key=True, default=generate_uuid)
    match_result_id = Column(String, ForeignKey("match_results.id"), nullable=False)
    requirement = Column(String, nullable=False)
    evidence = Column(Text, nullable=True)
    source = Column(String, nullable=True)  # Resume Section / Job Requirement
    match_type = Column(String, default="MATCHED")  # MATCHED, MISSING, PARTIAL
    importance = Column(String, default="REQUIRED")  # REQUIRED, PREFERRED
    
    # Relationships
    match_result = relationship("MatchResult", back_populates="evidences")
