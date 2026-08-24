# Smart Resume Screener — Architecture Blueprint

## System Architecture

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
  Resume Pipeline             JD Pipeline             Screening Engine
  (PyMuPDF / OCR)         (NLP Extraction)            (Deterministic + LLM)
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

## Core Components

### 1. Document Extraction Layer
- **PDF Parser (`fitz` / PyMuPDF)**: Extracts text blocks preserving reading order across multi-column layouts.
- **Scanned PDF Detection & OCR Fallback**: Automatically measures page character density. If text length < 50 characters, triggers pytesseract / OCR fallback parsing.

### 2. Skill Normalization Layer
Canonicalizes variations and aliases to prevent keyword mismatch:
- `Postgres`, `postgresql`, `postgres db` $\to$ `PostgreSQL`
- `ReactJS`, `react.js`, `react` $\to$ `React`
- `Node`, `node.js`, `nodejs` $\to$ `Node.js`
- `JS`, `javascript` $\to$ `JavaScript`
- `AWS EC2`, `amazon web services` $\to$ `AWS`

### 3. Multi-Layered Matching & Scoring Engine
Instead of relying blindly on an opaque LLM score, candidate fit is calculated using a transparent weighted multi-component formula:

$$\text{Overall Score} = 0.35 \cdot \text{ReqSkills} + 0.20 \cdot \text{Exp} + 0.15 \cdot \text{Resps} + 0.15 \cdot \text{Semantic} + 0.10 \cdot \text{Edu} + 0.05 \cdot \text{PrefSkills}$$

#### Critical Mandatory Penalty
If a candidate is missing any mandatory required skill or lacks at least $50\%$ of minimum required experience:
- `critical_requirement_missing` is set to `True`.
- Recommendation tier is capped to `PARTIAL_MATCH` or `WEAK_MATCH` regardless of high raw similarity.

### 4. Recommendation Tiers
- **`STRONG_MATCH`**: Score $\ge 85\%$ with zero missing mandatory requirements.
- **`MATCH`**: Score $70\% - 84\%$ with all mandatory requirements met.
- **`PARTIAL_MATCH`**: Score $55\% - 69\%$ OR candidate missing mandatory items.
- **`WEAK_MATCH`**: Score $< 55\%$.

### 5. Database Schema & Models
- `candidates`: Candidate Contact Info (Name, Email, Phone, Location, LinkedIn, GitHub).
- `resumes`: Raw Resume Text, Parser Status, OCR Used, Confidence, Structured JSON Profile.
- `jobs`: Job Title, Company, Raw Description, Structured JSON Requirements.
- `match_results`: Candidate ID, Job ID, Overall Score, Recommendation, Confidence, Breakdown, Strengths, Weaknesses, Critical Gaps, AI Explanation.
- `match_evidences`: Direct quoted evidence, matched section, importance tier (REQUIRED vs PREFERRED).
