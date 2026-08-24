import pytest
from app.matcher.skill_normalizer import SkillNormalizer


def test_skill_normalization_aliases():
    normalizer = SkillNormalizer()

    assert normalizer.normalize("postgres") == "PostgreSQL"
    assert normalizer.normalize("PostgreSQL") == "PostgreSQL"
    assert normalizer.normalize("react.js") == "React"
    assert normalizer.normalize("ReactJS") == "React"
    assert normalizer.normalize("aws ec2") == "AWS"
    assert normalizer.normalize("node") == "Node.js"
    assert normalizer.normalize("js") == "JavaScript"
    assert normalizer.normalize("spring boot") == "Spring Boot"


def test_normalize_list_deduplication():
    normalizer = SkillNormalizer()
    raw_list = ["Postgres", "postgresql", "ReactJS", "react", "Python", "PY"]
    normalized = normalizer.normalize_list(raw_list)

    assert "PostgreSQL" in normalized
    assert "React" in normalized
    assert "Python" in normalized
    assert len(normalized) == 3


def test_is_match():
    normalizer = SkillNormalizer()

    assert normalizer.is_match("Postgres", "PostgreSQL") is True
    assert normalizer.is_match("ReactJS", "react") is True
    assert normalizer.is_match("Python", "Java") is False
