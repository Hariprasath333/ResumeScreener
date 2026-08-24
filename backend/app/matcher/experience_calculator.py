import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class ExperienceCalculator:
    """Calculates total experience duration in years/months and evaluates against JD requirements."""

    MONTH_MAP = {
        "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
        "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
        "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
        "nov": 11, "november": 11, "dec": 12, "december": 12
    }

    def parse_date(self, date_str: Optional[str], default_is_now: bool = False) -> Optional[datetime]:
        """Parses various date strings into datetime objects."""
        if not date_str or not date_str.strip():
            return datetime.utcnow() if default_is_now else None

        clean = date_str.strip().lower()
        if clean in ["present", "current", "now", "today", "ongoing"]:
            return datetime.utcnow()

        # Match Year only e.g. 2021
        match_yr = re.search(r"\b(19\d{2}|20\d{2})\b", clean)
        year = int(match_yr.group(1)) if match_yr else None

        # Match Month e.g. Jan, January, 05, 5
        month = 1
        for m_name, m_val in self.MONTH_MAP.items():
            if m_name in clean:
                month = m_val
                break

        if year:
            return datetime(year, month, 1)
        return None

    def calculate_total_years(self, experiences: List[Dict]) -> float:
        """
        Calculates total years of work experience from a list of experience dicts/objects,
        accounting for duration_months field or date parsing.
        """
        if not experiences:
            return 0.0

        total_months = 0

        for exp in experiences:
            # Check if duration_months is explicitly provided
            duration = 0
            if isinstance(exp, dict):
                duration = exp.get("duration_months", 0)
                start_str = exp.get("start_date")
                end_str = exp.get("end_date")
            else:
                duration = getattr(exp, "duration_months", 0)
                start_str = getattr(exp, "start_date", None)
                end_str = getattr(exp, "end_date", None)

            if duration > 0:
                total_months += duration
            else:
                start_dt = self.parse_date(start_str)
                end_dt = self.parse_date(end_str, default_is_now=True)

                if start_dt and end_dt and end_dt >= start_dt:
                    diff_months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month) + 1
                    total_months += max(1, diff_months)

        return round(total_months / 12.0, 1)

    def evaluate_experience_score(self, candidate_years: float, required_years: float) -> Tuple[float, str]:
        """
        Evaluates candidate experience against job requirements.
        Returns:
            (score_percentage: 0-100, evidence_explanation: str)
        """
        if required_years <= 0:
            return (100.0, f"Candidate has {candidate_years} years of experience (No minimum required).")

        if candidate_years >= required_years:
            score = 100.0
            evidence = f"Candidate has {candidate_years} years of experience, exceeding the required {required_years} years."
        elif candidate_years >= required_years * 0.7:
            # Partial match (e.g. 2.5 yrs vs 3 yrs required)
            score = round((candidate_years / required_years) * 100, 1)
            evidence = f"Candidate has {candidate_years} years of experience, closely approaching the required {required_years} years."
        else:
            score = max(20.0, round((candidate_years / required_years) * 100, 1))
            evidence = f"Candidate has {candidate_years} years of experience, below the required {required_years} years."

        return (score, evidence)
