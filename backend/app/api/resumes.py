import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import CorruptedFileError, ResumeParsingError, ResumeNotFoundError
from app.database.connection import get_db
from app.models.base import Candidate, Resume
from app.parsers.pdf_parser import PDFParser
from app.parsers.text_parser import TextParser
from app.llm.client import LLMClient
from app.schemas.resume import ResumeUploadResponse, StructuredResume

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

pdf_parser = PDFParser()
text_parser = TextParser()
llm_client = LLMClient()


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse one or multiple PDF / TXT resumes.
    Returns array of extracted candidate profile responses.
    """
    results = []

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        # Parse Document
        try:
            if ext == ".pdf":
                parsed = pdf_parser.parse(content)
            else:
                parsed = text_parser.parse(content)
        except (CorruptedFileError, ResumeParsingError) as e:
            raise HTTPException(status_code=422, detail=f"File processing error in '{file.filename}': {e.message}")

        # Extract structured profile via LLM
        structured_profile: StructuredResume = llm_client.parse_resume(parsed["raw_text"])

        # Create Candidate record
        candidate = Candidate(
            name=structured_profile.candidate.name or "Candidate",
            email=structured_profile.candidate.email,
            phone=structured_profile.candidate.phone,
            location=structured_profile.candidate.location,
            linkedin=structured_profile.candidate.linkedin,
            github=structured_profile.candidate.github
        )
        db.add(candidate)
        db.flush()

        # Save resume file locally if upload dir configured
        file_path = os.path.join(settings.UPLOAD_DIR, f"{candidate.id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)

        # Create Resume record
        resume = Resume(
            candidate_id=candidate.id,
            file_name=file.filename,
            file_type=ext.replace(".", "").upper(),
            file_path=file_path,
            raw_text=parsed["raw_text"],
            parser_status="SUCCESS",
            ocr_used=parsed.get("ocr_used", False),
            extraction_confidence=parsed.get("confidence", 1.0),
            structured_data=structured_profile.model_dump()
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        results.append({
            "id": resume.id,
            "candidate_id": candidate.id,
            "file_name": resume.file_name,
            "file_type": resume.file_type,
            "parser_status": resume.parser_status,
            "ocr_used": resume.ocr_used,
            "extraction_confidence": resume.extraction_confidence,
            "structured_data": structured_profile,
            "created_at": resume.created_at
        })

    return results


@router.get("", response_model=List[dict])
def list_resumes(db: Session = Depends(get_db)):
    """List all uploaded resumes with candidate details."""
    resumes = db.query(Resume).all()
    out = []
    for r in resumes:
        cand = db.query(Candidate).filter(Candidate.id == r.candidate_id).first()
        out.append({
            "id": r.id,
            "candidate_id": r.candidate_id,
            "candidate_name": cand.name if cand else "Unknown",
            "file_name": r.file_name,
            "file_type": r.file_type,
            "parser_status": r.parser_status,
            "ocr_used": r.ocr_used,
            "created_at": r.created_at,
            "structured_data": r.structured_data
        })
    return out


@router.get("/{resume_id}")
def get_resume(resume_id: str, db: Session = Depends(get_db)):
    """Get single resume by ID."""
    r = db.query(Resume).filter(Resume.id == resume_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")
    cand = db.query(Candidate).filter(Candidate.id == r.candidate_id).first()
    return {
        "id": r.id,
        "candidate_id": r.candidate_id,
        "candidate_name": cand.name if cand else "Unknown",
        "file_name": r.file_name,
        "file_type": r.file_type,
        "raw_text": r.raw_text,
        "parser_status": r.parser_status,
        "ocr_used": r.ocr_used,
        "extraction_confidence": r.extraction_confidence,
        "structured_data": r.structured_data,
        "created_at": r.created_at
    }


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: str, db: Session = Depends(get_db)):
    """Delete resume and candidate."""
    r = db.query(Resume).filter(Resume.id == resume_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    cand = db.query(Candidate).filter(Candidate.id == r.candidate_id).first()
    db.delete(r)
    if cand:
        db.delete(cand)
    db.commit()
    return None
