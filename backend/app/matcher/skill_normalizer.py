import re
from typing import Dict, List, Set

# Standardized skill alias canonicalization dictionary
SKILL_ALIASES: Dict[str, str] = {
    # Programming Languages
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "js/ts": "JavaScript",
    "ecmascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "java": "Java",
    "java 8": "Java",
    "java 11": "Java",
    "java 17": "Java",
    "java 21": "Java",
    "cpp": "C++",
    "c++": "C++",
    "c#": "C#",
    "csharp": "C#",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "php": "PHP",
    "ruby": "Ruby",
    "kotlin": "Kotlin",
    "swift": "Swift",

    # Frameworks & Libraries
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "react js": "React",
    "next": "Next.js",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "expressjs": "Express.js",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "spring framework": "Spring Boot",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "dotnet": ".NET",
    ".net": ".NET",
    ".net core": ".NET Core",
    "asp.net": "ASP.NET",

    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "postgres db": "PostgreSQL",
    "pg": "PostgreSQL",
    "mysql": "MySQL",
    "my sql": "MySQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "mongo db": "MongoDB",
    "redis": "Redis",
    "sqlite": "SQLite",
    "dynamodb": "DynamoDB",
    "dynamo db": "DynamoDB",
    "oracle": "Oracle",
    "sql server": "MS SQL Server",
    "mssql": "MS SQL Server",
    "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch",

    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "aws ec2": "AWS",
    "aws s3": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "containerization": "Docker",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",

    # Architecture & Concepts
    "rest": "REST APIs",
    "restful": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "graphql": "GraphQL",
    "grpc": "gRPC",
    "microservices": "Microservices",
    "kafka": "Apache Kafka",
    "apache kafka": "Apache Kafka",
    "rabbitmq": "RabbitMQ",
    "sql": "SQL",
    "nosql": "NoSQL",

    # AI & ML
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs"
}


class SkillNormalizer:
    """Normalizes raw skill strings into standardized canonical representations."""

    def __init__(self, alias_dict: Dict[str, str] = None):
        self.alias_dict = alias_dict or SKILL_ALIASES

    def normalize(self, skill: str) -> str:
        """
        Normalizes a single skill string.
        Examples:
            'Postgres' -> 'PostgreSQL'
            'react.js' -> 'React'
            'aws ec2' -> 'AWS'
        """
        if not skill or not skill.strip():
            return ""

        clean = skill.strip().lower()
        # Clean punctuation wrapper e.g. (Postgres) -> postgres
        clean = re.sub(r"^[^\w\+\#\.]+|[^\w\+\#\.]+$", "", clean)

        if clean in self.alias_dict:
            return self.alias_dict[clean]

        # Try word replacement or fallback titlecase
        for key, val in self.alias_dict.items():
            if clean == key:
                return val

        # Capitalize nicely if not in dictionary
        return skill.strip().title()

    def normalize_list(self, skills: List[str]) -> List[str]:
        """Normalizes a list of skills and removes duplicates while preserving order."""
        seen: Set[str] = set()
        normalized = []

        for skill in skills:
            norm = self.normalize(skill)
            if norm and norm.lower() not in seen:
                seen.add(norm.lower())
                normalized.append(norm)

        return normalized

    def is_match(self, skill1: str, skill2: str) -> bool:
        """Determines if two raw skill strings refer to the same canonical skill."""
        n1 = self.normalize(skill1).lower()
        n2 = self.normalize(skill2).lower()
        if n1 == n2:
            return True
        # Check substring containment e.g. "kafka" in "apache kafka"
        return n1 in n2 or n2 in n1
