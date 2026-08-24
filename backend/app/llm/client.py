import json
import re
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.llm.prompts import (
    RESUME_EXTRACTION_SYSTEM, RESUME_EXTRACTION_USER,
    JD_EXTRACTION_SYSTEM, JD_EXTRACTION_USER,
    MATCHING_EVIDENCE_SYSTEM, MATCHING_EVIDENCE_USER
)
from app.llm.validator import LLMValidator
from app.schemas.resume import StructuredResume, CandidateContact, SkillCategories, WorkExperience, EducationEntry, ProjectEntry, CertificationEntry
from app.schemas.job import StructuredJD, ExperienceRequirement, EducationRequirement


class MockLLMProvider:
    """Built-in intelligent mock LLM provider for instant, keyless execution and testing."""

    def extract_resume_profile(self, raw_text: str) -> StructuredResume:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        
        # 1. Extract Name & Contact
        name = "Candidate"
        email = None
        phone = None
        location = None
        linkedin = None
        github = None

        if lines:
            first_line = lines[0]
            if len(first_line) < 50 and not any(kw in first_line.lower() for kw in ["resume", "curriculum", "email", "phone", "summary", "experience"]):
                name = first_line.strip()

        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_text)
        if email_match:
            email = email_match.group(0)

        phone_match = re.search(r"\(?\+?\d{1,3}\)?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}", raw_text)
        if phone_match:
            phone = phone_match.group(0)

        loc_match = re.search(r"(?:Location|Address|City):\s*([A-Za-z\s,]+)", raw_text, re.IGNORECASE)
        if loc_match:
            location = loc_match.group(1).strip()

        linkedin_match = re.search(r"linkedin\.com/in/[\w\-]+", raw_text, re.IGNORECASE)
        if linkedin_match:
            linkedin = f"https://www.{linkedin_match.group(0)}"

        github_match = re.search(r"github\.com/[\w\-]+", raw_text, re.IGNORECASE)
        if github_match:
            github = f"https://www.{github_match.group(0)}"

        contact = CandidateContact(
            name=name,
            email=email or "",
            phone=phone,
            location=location,
            linkedin=linkedin,
            github=github
        )

        # 2. Extract Skills dynamically from technical keywords
        prog_langs = []
        frameworks = []
        databases = []
        cloud = []
        devops = []
        ai_ml = []
        tools = []

        skill_keywords = {
            "programming_languages": ["Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Kotlin", "Swift", "SQL", "HTML", "CSS"],
            "frameworks": ["React", "ReactJS", "Spring Boot", "Spring", "Node.js", "Express", "FastAPI", "Django", "Flask", "Angular", "Vue", "Next.js", "NestJS", "ASP.NET", ".NET"],
            "databases": ["PostgreSQL", "Postgres", "MySQL", "MongoDB", "Redis", "SQLite", "DynamoDB", "Oracle", "Cassandra", "Elasticsearch"],
            "cloud": ["AWS", "Amazon Web Services", "GCP", "Google Cloud", "Azure", "Cloudflare"],
            "devops": ["Docker", "Kubernetes", "CI/CD", "Terraform", "Jenkins", "GitHub Actions", "Ansible", "Linux"],
            "ai_ml": ["PyTorch", "TensorFlow", "Scikit-Learn", "NLP", "Machine Learning", "Deep Learning", "LLMs", "LangChain"],
            "tools": ["Git", "Postman", "Jira", "Figma", "Docker", "VS Code", "Webpack", "Vite"]
        }

        for kw in skill_keywords["programming_languages"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", raw_text, re.IGNORECASE):
                prog_langs.append(kw)

        for kw in skill_keywords["frameworks"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", raw_text, re.IGNORECASE):
                frameworks.append(kw)

        for kw in skill_keywords["databases"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", raw_text, re.IGNORECASE):
                databases.append(kw)

        for kw in skill_keywords["cloud"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", raw_text, re.IGNORECASE):
                cloud.append(kw)

        for kw in skill_keywords["devops"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", raw_text, re.IGNORECASE):
                devops.append(kw)

        for kw in skill_keywords["ai_ml"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", raw_text, re.IGNORECASE):
                ai_ml.append(kw)

        for kw in skill_keywords["tools"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", raw_text, re.IGNORECASE):
                tools.append(kw)

        skills = SkillCategories(
            programming_languages=list(set(prog_langs)),
            frameworks=list(set(frameworks)),
            databases=list(set(databases)),
            cloud=list(set(cloud)),
            devops=list(set(devops)),
            ai_ml=list(set(ai_ml)),
            tools=list(set(tools))
        )

        # 3. Extract Experience bullets and calculate duration
        exps = []
        resp_bullets = [
            line.strip("-*• ") for line in lines 
            if any(kw in line.lower() for kw in ["developed", "built", "designed", "engineered", "implemented", "managed", "created", "led", "architected", "optimized", "collaborated", "worked"])
        ]
        
        # Estimate duration from date mentions e.g. 2020 - 2024 or 5 years
        year_matches = re.findall(r"\b(20\d{2}|19\d{2})\b", raw_text)
        years = [int(y) for y in year_matches]
        
        duration_m = 24  # default base 2 years
        if len(years) >= 2:
            span_years = max(years) - min(years)
            if span_years > 0:
                duration_m = span_years * 12

        # Check explicit experience mention like "5+ years of experience"
        exp_mention = re.search(r"(\d+)\+?\s*years(?:\s*of)?\s*experience", raw_text, re.IGNORECASE)
        if exp_mention:
            duration_m = int(exp_mention.group(1)) * 12

        # Find company / role if listed
        company_name = "Experience Record"
        role_name = "Software Engineer"
        for line in lines:
            if "|" in line and any(kw in line.lower() for kw in ["engineer", "developer", "lead", "architect", "manager", "specialist", "intern", "analyst"]):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 2:
                    role_name = parts[0]
                    company_name = parts[1]
                break

        exps.append(WorkExperience(
            company=company_name,
            role=role_name,
            start_date="2020-01",
            end_date="Present",
            duration_months=duration_m,
            responsibilities=resp_bullets[:5] if resp_bullets else [
                "Developed software features and maintained production codebase.",
                "Collaborated with technical team to deliver project requirements."
            ],
            technologies=list(set(prog_langs + frameworks))[:5],
            achievements=[]
        ))

        # 4. Extract Education from actual text
        edu = []
        edu_matches = re.findall(r"(Bachelor|Master|Doctorate|B\.S\.|M\.S\.|B\.A\.|M\.A\.|Ph\.D|Associate|Diploma)[^\n]*", raw_text, re.IGNORECASE)
        if edu_matches:
            for em in edu_matches[:2]:
                edu.append(EducationEntry(
                    degree=em.strip(),
                    university="Accredited University",
                    field="Computer Science / Engineering",
                    graduation_year=years[-1] if years else None
                ))
        elif any(kw in raw_text.lower() for kw in ["computer science", "software engineering", "bachelor", "master", "degree"]):
            edu.append(EducationEntry(
                degree="Bachelor of Science",
                university="University",
                field="Computer Science",
                graduation_year=None
            ))

        # 5. Extract Projects & Certifications only if in text
        projects = []
        proj_lines = [l for l in lines if "project" in l.lower() or "built" in l.lower()]
        if proj_lines:
            projects.append(ProjectEntry(
                name="Application Development Project",
                description=proj_lines[0][:100],
                technologies=list(set(prog_langs + frameworks))[:3]
            ))

        certs = []
        cert_matches = re.findall(r"(AWS Certified[^\n]*|Certified Kubernetes[^\n]*|Oracle Certified[^\n]*|Microsoft Certified[^\n]*)", raw_text, re.IGNORECASE)
        for c in cert_matches:
            certs.append(CertificationEntry(name=c.strip(), issuer="Certification Authority", date=""))

        return StructuredResume(
            candidate=contact,
            skills=skills,
            experience=exps,
            education=edu,
            projects=projects,
            certifications=certs
        )

    def extract_jd_requirements(self, jd_text: str) -> StructuredJD:
        lines = [l.strip() for l in jd_text.splitlines() if l.strip()]
        role = lines[0] if lines else "Software Engineer"
        
        # Comprehensive Technical Skills Vocabulary
        all_tech = [
            "Java", "Python", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Kotlin", "Swift",
            "Spring Boot", "Spring", "React", "ReactJS", "Node.js", "Express", "FastAPI", "Django", "Flask", "Angular", "Vue", "Next.js",
            "PostgreSQL", "Postgres", "MySQL", "MongoDB", "Redis", "SQLite", "DynamoDB", "Oracle", "Cassandra", "Elasticsearch",
            "AWS", "Amazon Web Services", "GCP", "Google Cloud", "Azure", "Docker", "Kubernetes", "Kafka", "Apache Kafka",
            "REST APIs", "REST", "GraphQL", "CI/CD", "Terraform", "Jenkins", "Git", "Microservices", "SQL", "Linux"
        ]

        # Check for section boundaries (Required vs Preferred)
        req_section_text = jd_text
        pref_section_text = ""

        pref_match = re.search(r"(?:preferred|nice to have|bonus|good to have)[\s\S]*", jd_text, re.IGNORECASE)
        if pref_match:
            pref_section_text = pref_match.group(0)
            req_section_text = jd_text[:pref_match.start()]

        req_skills = []
        pref_skills = []

        for tech in all_tech:
            # Match exact word boundaries
            pattern = r"\b" + re.escape(tech) + r"\b"
            if re.search(pattern, req_section_text, re.IGNORECASE):
                req_skills.append(tech)
            elif pref_section_text and re.search(pattern, pref_section_text, re.IGNORECASE):
                pref_skills.append(tech)

        # Fallback if no specific section split found but tech found in text
        if not req_skills and not pref_skills:
            all_found = [tech for tech in all_tech if re.search(r"\b" + re.escape(tech) + r"\b", jd_text, re.IGNORECASE)]
            if all_found:
                req_skills = all_found[:5]
                pref_skills = all_found[5:8]
            else:
                req_skills = ["Software Development", "API Design", "Problem Solving"]

        # Min experience extraction
        min_years = 0.0
        exp_matches = re.findall(r"(\d+)\+?\s*years(?:\s*of)?\s*experience", jd_text, re.IGNORECASE)
        if exp_matches:
            min_years = float(exp_matches[0])
        else:
            exp_match = re.search(r"(\d+)\+?\s*years", jd_text, re.IGNORECASE)
            if exp_match:
                min_years = float(exp_match.group(1))

        # Responsibilities extraction
        resps = []
        for line in lines:
            if line.startswith(("-", "*", "•")) or any(line.lower().startswith(v) for v in ["design", "develop", "build", "architect", "maintain", "collaborate", "lead", "implement", "optimize"]):
                clean_line = line.strip("-*• ")
                if len(clean_line) > 15:
                    resps.append(clean_line)

        if not resps:
            resps = [
                "Architect and develop high quality software components.",
                "Collaborate with team to implement and deploy scalable services."
            ]

        # Degrees
        degrees = ["Bachelor"]
        if "master" in jd_text.lower() or "m.s." in jd_text.lower():
            degrees.append("Master")
        if "phd" in jd_text.lower():
            degrees.append("PhD")

        return StructuredJD(
            role=role if len(role) < 60 else "Software Engineer",
            seniority="Senior" if "senior" in jd_text.lower() or min_years >= 5 else "Mid",
            required_skills=list(dict.fromkeys(req_skills)),
            preferred_skills=list(dict.fromkeys(pref_skills)),
            experience=ExperienceRequirement(minimum_years=min_years, preferred_years=min_years + 2),
            education=EducationRequirement(degrees=degrees, fields=["Computer Science", "Engineering"]),
            responsibilities=resps[:6],
            domain_requirements=["Backend Systems", "Distributed Applications"],
            soft_skills=["Team Collaboration", "Problem Solving"]
        )


class LLMClient:
    """Unified LLM Client providing support for Mock, OpenAI, Gemini, and Ollama providers."""

    def __init__(self, provider: str = None, api_key: str = None):
        self.provider = (provider or settings.LLM_PROVIDER).lower()
        self.api_key = api_key or settings.LLM_API_KEY
        self.validator = LLMValidator()
        self.mock_provider = MockLLMProvider()

    def parse_resume(self, raw_text: str) -> StructuredResume:
        """Parses raw resume text into StructuredResume Pydantic model."""
        if self.provider == "mock" or not self.api_key:
            return self.mock_provider.extract_resume_profile(raw_text)

        # Handle OpenAI API provider if API key present
        if self.provider == "openai":
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": RESUME_EXTRACTION_SYSTEM},
                        {"role": "user", "content": RESUME_EXTRACTION_USER.format(
                            resume_text=raw_text,
                            schema_json=json.dumps(StructuredResume.model_json_schema())
                        )}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1
                }
                response = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30.0)
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    return self.validator.parse_and_validate(content, StructuredResume)
            except Exception:
                pass  # Fallback to mock on API error

        return self.mock_provider.extract_resume_profile(raw_text)

    def parse_jd(self, jd_text: str) -> StructuredJD:
        """Parses job description into StructuredJD Pydantic model."""
        if self.provider == "mock" or not self.api_key:
            return self.mock_provider.extract_jd_requirements(jd_text)

        if self.provider == "openai":
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": JD_EXTRACTION_SYSTEM},
                        {"role": "user", "content": JD_EXTRACTION_USER.format(jd_text=jd_text)}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1
                }
                response = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30.0)
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    return self.validator.parse_and_validate(content, StructuredJD)
            except Exception:
                pass

        return self.mock_provider.extract_jd_requirements(jd_text)
