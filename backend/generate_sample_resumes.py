import os
try:
    import pymupdf as fitz
except ImportError:
    import fitz

resumes_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "resumes")
os.makedirs(resumes_dir, exist_ok=True)

resumes_data = [
    {
        "filename": "sample_lead_java_alex.txt",
        "pdf_filename": "sample_lead_java_alex.pdf",
        "text": """Alex Mercer
Email: alex.mercer@devtech.io
Phone: +1 (555) 234-5678
Location: Austin, TX
LinkedIn: linkedin.com/in/alexmercer-dev
GitHub: github.com/alexmercer

SUMMARY:
Lead Backend Engineer with 6+ years of production experience architecting mission-critical Java Spring Boot microservices, high-throughput Apache Kafka event pipelines, and scalable PostgreSQL database clusters on AWS.

TECHNICAL SKILLS:
- Programming Languages: Java, Python, SQL, Go
- Frameworks & Libraries: Spring Boot, Spring Cloud, Hibernate, FastAPI
- Databases: PostgreSQL, Redis, MySQL, DynamoDB
- Cloud & DevOps: AWS (EC2, S3, RDS, Lambda), Docker, Kubernetes, CI/CD, Terraform
- Architecture: REST APIs, Apache Kafka, Microservices, Event-Driven Architecture

PROFESSIONAL EXPERIENCE:
Lead Software Engineer | FinTech Cloud Systems | Austin, TX
Jan 2022 - Present (2.5 years)
- Architected enterprise Spring Boot REST microservices processing over $50M daily transactions.
- Designed distributed real-time messaging pipeline utilizing Apache Kafka and PostgreSQL.
- Reduced API latency by 45% using Redis caching and PostgreSQL query optimization.
- Led cloud migration of legacy monolith to containerized Kubernetes services on AWS.

Senior Backend Engineer | CloudScale Tech | San Jose, CA
Jun 2018 - Dec 2021 (3.5 years)
- Developed Java REST APIs for e-commerce payment processing platform.
- Managed PostgreSQL database schema migrations and automated backups.
- Integrated Docker and GitHub Actions CI/CD pipelines.

EDUCATION:
Bachelor of Science in Computer Science
University of Texas at Austin (2018) | GPA: 3.9 / 4.0

CERTIFICATIONS:
AWS Certified Solutions Architect - Professional (2023)
"""
    },
    {
        "filename": "sample_mid_java_sarah.txt",
        "pdf_filename": "sample_mid_java_sarah.pdf",
        "text": """Sarah Jenkins
Email: sarah.jenkins@codeflow.io
Phone: +1 (555) 876-5432
Location: Denver, CO
LinkedIn: linkedin.com/in/sarahjenkins-dev

SUMMARY:
Software Engineer with 3.5 years of experience developing robust backend services using Java, Spring Boot, REST APIs, and PostgreSQL. Passionate about clean code and API performance.

TECHNICAL SKILLS:
- Languages: Java, SQL, JavaScript
- Frameworks: Spring Boot, Spring MVC, REST APIs
- Databases: PostgreSQL, MySQL, SQLite
- Tools & Cloud: Docker, Git, Postman, Linux

PROFESSIONAL EXPERIENCE:
Java Backend Developer | DataWorks Solutions | Denver, CO
Mar 2021 - Present (3.5 years)
- Developed secure Spring Boot REST APIs for customer portal applications.
- Engineered PostgreSQL database schemas and optimized indexing for query speed.
- Collaborated with frontend team to integrate backend API endpoints.
- Conducted unit and integration testing achieving 85% test coverage.

EDUCATION:
Bachelor of Science in Software Engineering
Colorado State University (2021) | GPA: 3.7 / 4.0
"""
    },
    {
        "filename": "sample_frontend_david.txt",
        "pdf_filename": "sample_frontend_david.pdf",
        "text": """David Chen
Email: david.chen@webcraft.dev
Phone: +1 (555) 345-6789
Location: Seattle, WA
LinkedIn: linkedin.com/in/davidchen-ui
GitHub: github.com/davidchen-ui

SUMMARY:
Frontend Engineer with 4 years of experience specializing in React, TypeScript, Next.js, and modern UI architecture.

TECHNICAL SKILLS:
- Languages: TypeScript, JavaScript, HTML5, CSS3
- Frameworks: React, Next.js, Vue.js, Tailwind CSS
- Tools: Vite, Webpack, Git, Figma, Jest

PROFESSIONAL EXPERIENCE:
Senior Frontend Developer | Nova UI Studios | Seattle, WA
Jan 2022 - Present (2.5 years)
- Built interactive dashboard interfaces using React, TypeScript, and Tailwind CSS.
- Optimized frontend bundle size and web vitals performance scores.
- Implemented state management using Zustand and React Query.

Frontend Developer | PixelCraft Media | Seattle, WA
Jun 2020 - Dec 2021 (1.5 years)
- Developed responsive web applications using React and CSS modules.
- Created reusable component libraries for design systems.

EDUCATION:
Bachelor of Arts in Interactive Digital Media
University of Washington (2020)
"""
    }
]

for item in resumes_data:
    txt_path = os.path.join(resumes_dir, item["filename"])
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(item["text"].strip())
    print(f"Wrote text resume: {txt_path}")

    # Generate PDF
    pdf_path = os.path.join(resumes_dir, item["pdf_filename"])
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4
    
    # Write styled text onto PDF page
    rect = fitz.Rect(50, 50, 545, 792)
    page.insert_textbox(rect, item["text"].strip(), fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))
    doc.save(pdf_path)
    doc.close()
    print(f"Generated PDF resume: {pdf_path}")

print("Successfully generated all sample test resumes (TXT and PDF)!")
