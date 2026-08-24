from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.base import Job
from app.llm.client import LLMClient
from app.schemas.job import JobCreate, JobResponse, StructuredJD

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])
llm_client = LLMClient()


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    """
    Create a new Job Description and extract structured requirements (Required vs Preferred skills, Min experience, Education).
    """
    structured_reqs: StructuredJD = llm_client.parse_jd(job_in.description)

    job = Job(
        title=job_in.title or structured_reqs.role,
        company=job_in.company or "TechCorp",
        description=job_in.description,
        structured_requirements=structured_reqs.model_dump()
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get("", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    """List all job postings."""
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get job posting detail by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Delete job description by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    db.delete(job)
    db.commit()
    return None
