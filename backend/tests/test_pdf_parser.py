import os
import pytest
from app.parsers.pdf_parser import PDFParser
from app.core.exceptions import CorruptedFileError, ResumeParsingError

def test_pdf_parser_valid_file():
    parser = PDFParser()
    sample_pdf = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "resumes", "sample_lead_java_alex.pdf"))
    
    assert os.path.exists(sample_pdf), f"Sample PDF missing at {sample_pdf}"
    
    with open(sample_pdf, "rb") as f:
        content = f.read()
        
    result = parser.parse(content)
    assert result["pages_count"] >= 1
    assert len(result["raw_text"]) > 100
    assert "Alex Mercer" in result["raw_text"]
    assert "Spring Boot" in result["raw_text"]
    assert result["ocr_used"] is False
    assert result["confidence"] == 1.0

def test_pdf_parser_corrupted_file():
    parser = PDFParser()
    corrupted_bytes = b"This is not a valid PDF content header"
    
    with pytest.raises((CorruptedFileError, ResumeParsingError)):
        parser.parse(corrupted_bytes)
