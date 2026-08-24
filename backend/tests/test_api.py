import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import init_db

# Initialize database tables for tests
init_db()

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Smart Resume Screener" in data["app_name"]


def test_create_and_get_job():
    payload = {
        "title": "Senior Java Developer",
        "company": "Enterprise Tech",
        "description": "Looking for a Senior Java Developer with 4+ years experience in Spring Boot, REST APIs, PostgreSQL, and AWS."
    }
    create_resp = client.post("/api/jobs", json=payload)
    assert create_resp.status_code == 201
    job_data = create_resp.json()
    assert job_data["id"] is not None
    assert job_data["title"] == "Senior Java Developer"
    assert "structured_requirements" in job_data

    # Retrieve created job
    get_resp = client.get(f"/api/jobs/{job_data['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == job_data["id"]


def test_upload_resume_txt():
    sample_text = """
    Alice Johnson
    Email: alice.johnson@example.com
    Phone: +1 555-0199
    
    SKILLS:
    Java, Spring Boot, PostgreSQL, REST APIs, Docker, Git
    
    EXPERIENCE:
    Senior Software Engineer — TechCorp (2020 - Present)
    - Developed high throughput RESTful services using Java and Spring Boot.
    - Managed production PostgreSQL database queries and indexing.
    - Containerized microservices using Docker.
    
    EDUCATION:
    B.S. in Computer Science — Stanford University (2020)
    """

    file_tuple = ("resume_alice.txt", io.BytesIO(sample_text.encode("utf-8")), "text/plain")
    upload_resp = client.post("/api/resumes", files={"files": file_tuple})
    assert upload_resp.status_code == 201
    res_list = upload_resp.json()
    assert len(res_list) == 1
    resume_obj = res_list[0]
    assert resume_obj["file_name"] == "resume_alice.txt"
    assert resume_obj["structured_data"] is not None


def test_full_screening_and_ranking_flow():
    # 1. Create Job
    job_resp = client.post("/api/jobs", json={
        "title": "Backend Java Engineer",
        "company": "FinTech Corp",
        "description": "Requires Java, Spring Boot, PostgreSQL, REST APIs with 2+ years experience."
    })
    job_id = job_resp.json()["id"]

    # 2. Upload Resume
    resume_text = """
    Bob Smith
    Email: bob@example.com
    Skills: Java, Spring Boot, PostgreSQL, REST APIs
    Experience: 3 years as Java Backend Developer building REST APIs with Spring Boot.
    Education: BS Computer Science
    """
    file_tuple = ("bob_resume.txt", io.BytesIO(resume_text.encode("utf-8")), "text/plain")
    client.post("/api/resumes", files={"files": file_tuple})

    # 3. Trigger Candidate Screening
    screen_resp = client.post(f"/api/jobs/{job_id}/screen")
    assert screen_resp.status_code == 200
    screen_data = screen_resp.json()
    assert screen_data["screened_count"] >= 1

    # 4. Fetch Ranked Candidates List
    candidates_resp = client.get(f"/api/jobs/{job_id}/candidates")
    assert candidates_resp.status_code == 200
    candidates = candidates_resp.json()
    assert len(candidates) >= 1
    first_candidate = candidates[0]
    assert first_candidate["rank"] == 1
    assert first_candidate["overall_score"] > 0
