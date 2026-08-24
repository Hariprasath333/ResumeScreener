import pytest
from app.matcher.experience_calculator import ExperienceCalculator


def test_experience_calculation_total_years():
    calc = ExperienceCalculator()

    experiences = [
        {"duration_months": 24, "role": "Backend Engineer"},
        {"duration_months": 12, "role": "Junior Developer"}
    ]

    total_years = calc.calculate_total_years(experiences)
    assert total_years == 3.0


def test_experience_evaluation_against_requirements():
    calc = ExperienceCalculator()

    # Exceeds requirement
    score, msg = calc.evaluate_experience_score(candidate_years=5.0, required_years=3.0)
    assert score == 100.0
    assert "exceeding" in msg

    # Meets requirement
    score, msg = calc.evaluate_experience_score(candidate_years=3.0, required_years=3.0)
    assert score == 100.0

    # Below requirement
    score, msg = calc.evaluate_experience_score(candidate_years=1.0, required_years=3.0)
    assert score < 70.0
    assert "below" in msg
