# Smart Resume Screener 
Deployed Link : https://resumescreener-oitz.onrender.com/

An enterprise-grade, technically rigorous **Smart Resume Screener** system featuring automated structured document extraction, skill alias normalization, multi-layered deterministic scoring with mandatory requirement penalties, semantic similarity matching, LLM evidence reasoning, and an interactive recruiter dashboard.

---

## 1. Problem Statement
Traditional ATS (Applicant Tracking Systems) suffer from two major flaws:
1. **Keyword Overweighting**: Candidates stuffing buzzwords rank high regardless of actual experience depth.
2. **Opaque AI Scoring**: Raw LLM wrappers returning a single "82% match" score fail to explain *why* a candidate fits or what mandatory requirements are missing.

## 2. Solution
Smart Resume Screener decouples document parsing, skill normalization, deterministic mathematical scoring, semantic similarity, and LLM reasoning into a transparent, audit-ready pipeline with exact quoted evidence.

---

## 3. Key Features
- 📄 **Multi-Format Extraction**: Parses PDF (`PyMuPDF`) and TXT files with layout-aware reading order and OCR fallback.
- 🔄 **Skill Normalization**: Automatically resolves aliases (`Postgres` $\to$ `PostgreSQL`, `ReactJS` $\to$ `React`, `AWS EC2` $\to$ `AWS`).
- 🧮 **Multi-Component Scoring Formula**: Weighted evaluation across Required Skills (35%), Experience (20%), Responsibilities (15%), Semantic Match (15%), Education (10%), and Preferred Skills (5%).
- ⚠️ **Critical Requirement Penalty**: Enforces mandatory qualification rules. Candidates missing mandatory required skills receive penalty flags and capped recommendation tiers (`PARTIAL_MATCH`).
- 🔍 **Evidence-Based Matching**: Extracts exact quoted evidence from candidate resumes mapping directly to job requirements.
- 🛡️ **PII Guardrails**: Masks sensitive personal attributes to mitigate unconscious bias.
- 📊 **Recruiter Dashboard**: React + Vite + Tailwind UI showing candidate rankings, score radar breakdowns, and evidence cards.
- 🧪 **Benchmark Evaluation & Test Suite**: Pytest test suite and evaluation script computing Precision, Recall, and F1.

---

## 4. Architecture

```
                    ┌──────────────────────────────┐
                    │      Recruiter Dashboard     │
                    │      (React + Tailwind)      │
                    └──────────────┬───────────────┘
                                   │ REST API calls
                                   ▼
                    ┌──────────────────────────────┐
                    │     FastAPI Backend API      │
                    └──────────────┬───────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
  Resume Processing            JD Processing         Screening & Match Engine
  (PyMuPDF / OCR)            (Structured NLP)        (Deterministic + LLM)
         │                         │                         │
         ▼                         ▼                         │
 Structured Resume          Structured JD                    │
 Profile (Pydantic)        Profile (Pydantic)                │
         │                         │                         │
         └────────────┬────────────┘                         │
                      ▼                                      │
           Skill Normalizer (Aliases)                        │
                      ▼                                      │
        Deterministic Scorer (35% Skills, 20% Exp...) ◄──────┘
                      ▼
         Semantic Similarity (TF-IDF Cosine)
                      ▼
       LLM Evidence Reasoning & Mandatory Penalty
                      ▼
      Candidate Ranking & Persistence (SQLAlchemy)
```

---

## 5. AI Pipeline
1. **Document Ingestion**: File validation (extension, size, corruption check).
2. **Text Extraction**: Block-level PDF text extraction via PyMuPDF.
3. **Structured Extraction**: Transforms raw text into Pydantic JSON schema (`StructuredResume` & `StructuredJD`).
4. **Skill Normalization**: Replaces skill aliases with canonical standard symbols.
5. **Deterministic & Semantic Match**: Calculates component scores and checks mandatory requirements.
6. **LLM Evidence Reasoning**: Extracts quotes and generates transparent summary.
7. **Pydantic Validation**: Validates output constraints and saves to database.

---

## 6. Tech Stack
- **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic v2
- **Database & ORM**: SQLAlchemy 2.0, SQLite / PostgreSQL
- **PDF & NLP**: PyMuPDF (`fitz`), scikit-learn (TF-IDF), pytesseract
- **LLM Integration**: Unified Client supporting OpenAI, Google Gemini, Ollama, and built-in Mock provider
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Axios
- **Testing & Eval**: Pytest, Pytest-Asyncio, Custom Evaluation Benchmark

---

## 7. Project Structure
```
smart-resume-screener/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI REST endpoints (resumes, jobs, matches)
│   │   ├── core/         # Config, settings, and custom exceptions
│   │   ├── database/     # SQLAlchemy connection & session management
│   │   ├── llm/          # Unified LLM client, prompts, and validator
│   │   ├── matcher/      # Skill normalizer, exp calculator, semantic matcher, scorer
│   │   ├── models/       # DB models (Candidate, Resume, Job, MatchResult, MatchEvidence)
│   │   ├── parsers/      # PyMuPDF PDF parser, text parser, extractors
│   │   ├── ranking/      # Candidate ranker & filter engine
│   │   └── schemas/      # Pydantic schemas (Resume, Job, Match)
│   ├── tests/            # Pytest unit & integration test suite
│   └── requirements.txt
├── frontend/             # React + Vite + Tailwind CSS Recruiter Dashboard
├── data/sample/          # Sample benchmark PDF/TXT resumes and JDs
├── evaluation/           # Evaluation script computing Precision, Recall, F1
├── docs/                 # Architecture, prompts, and evaluation docs
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 8. Database Schema
- **`candidates`**: `id`, `name`, `email`, `phone`, `location`, `linkedin`, `github`, `created_at`
- **`resumes`**: `id`, `candidate_id`, `file_name`, `file_type`, `raw_text`, `parser_status`, `ocr_used`, `structured_data`, `created_at`
- **`jobs`**: `id`, `title`, `company`, `description`, `structured_requirements`, `created_at`
- **`match_results`**: `id`, `candidate_id`, `job_id`, `overall_score`, `recommendation`, `scores_breakdown`, `strengths`, `weaknesses`, `critical_gaps`, `explanation`
- **`match_evidences`**: `id`, `match_result_id`, `requirement`, `evidence`, `match_type`, `importance`

---

## 9. API Documentation
- `POST /api/resumes` — Upload PDF/TXT resume and extract structured profile.
- `GET /api/resumes` — List uploaded resumes.
- `POST /api/jobs` — Create Job Description and auto-extract structured requirements.
- `GET /api/jobs` — List job positions.
- `POST /api/jobs/{id}/screen` — Run candidate screening engine for a job description.
- `GET /api/jobs/{id}/candidates` — Get ranked shortlist with filter parameters (`min_score`, `recommendation`, `require_all_mandatory`).
- `GET /api/matches/{id}` — Get candidate match details with score breakdown radar and evidence quotes.

---

## 10. LLM Prompts
Full prompt documentation available in [`docs/prompts.md`](file:///c:/Users/harip/Documents/SmartResumeScreener/docs/prompts.md).
- **Resume Extraction**: Enforces zero-hallucination factual extraction matching Pydantic schema.
- **JD Requirements Extraction**: Separates mandatory required skills from preferred qualifications.
- **Evidence-Based Matching**: Extracts exact quoted text from resume as empirical proof.

---

## 11. Matching Algorithm & Scoring Formula

$$\text{Overall Score} = 0.35 \cdot \text{ReqSkills} + 0.20 \cdot \text{Exp} + 0.15 \cdot \text{Resps} + 0.15 \cdot \text{Semantic} + 0.10 \cdot \text{Edu} + 0.05 \cdot \text{PrefSkills}$$

---

## 12. Recommendation Categories
- **`STRONG_MATCH`** (85-100): High alignment across skills & experience; zero mandatory gaps.
- **`MATCH`** (70-84): Meets all core requirements.
- **`PARTIAL_MATCH`** (55-69): Candidate missing mandatory required skill or experience.
- **`WEAK_MATCH`** (<55): Low alignment.

---

## 13. Sample Output

```json
{
  "candidate_name": "Alex Mercer",
  "job_title": "Senior Java Backend Developer",
  "overall_score": 92.5,
  "recommendation": "STRONG_MATCH",
  "scores": {
    "required_skills": 100.0,
    "experience": 100.0,
    "responsibilities": 88.0,
    "semantic_match": 85.0,
    "education": 100.0,
    "preferred_skills": 66.7
  },
  "matched_requirements": [
    {
      "requirement": "Java",
      "evidence": "Candidate possesses skill 'Java' explicitly listed in resume.",
      "match_type": "MATCHED",
      "importance": "REQUIRED"
    }
  ]
}
```

---

## 14. Quick Start & Execution

### 1. Setup Backend
```bash
cd backend
py -3.12 -m venv venv
venv/Scripts/python -m pip install -r requirements.txt
venv/Scripts/python -m app.main
```
Backend API will start at `http://localhost:8000`. API Docs available at `http://localhost:8000/docs`.

### 2. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```
Recruiter UI will start at `http://localhost:5173`.

### 3. Run Automated Tests
```bash
cd backend
venv/Scripts/python -m pytest -v
```

### 4. Run Evaluation Benchmark
```bash
venv/Scripts/python evaluation/eval_script.py
```

---

## 15. Docker Deployment
```bash
docker-compose up --build
```

---

## 16. Security & Privacy
- **API Key Confidentiality**: All API keys configured via environment variables (`.env`).
- **PII Guardrails**: Candidate contact details isolated from matching prompt.
- **Input Validation**: Strict MIME type checking and file size bounds.
