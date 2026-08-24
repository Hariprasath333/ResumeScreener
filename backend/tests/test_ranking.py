import pytest
from app.ranking.ranker import CandidateRanker

def test_candidate_ranking_order():
    ranker = CandidateRanker()
    candidates = [
        {"match_id": "1", "candidate_name": "Candidate A", "overall_score": 75.0, "recommendation": "MATCH", "critical_requirement_missing": False},
        {"match_id": "2", "candidate_name": "Candidate B", "overall_score": 92.0, "recommendation": "STRONG_MATCH", "critical_requirement_missing": False},
        {"match_id": "3", "candidate_name": "Candidate C", "overall_score": 50.0, "recommendation": "WEAK_MATCH", "critical_requirement_missing": True}
    ]
    
    ranked = ranker.rank_candidates(candidates)
    assert len(ranked) == 3
    assert ranked[0].rank == 1
    assert ranked[0].candidate_name == "Candidate B"
    assert ranked[0].overall_score == 92.0
    assert ranked[1].rank == 2
    assert ranked[1].candidate_name == "Candidate A"
    assert ranked[2].rank == 3
    assert ranked[2].candidate_name == "Candidate C"

def test_candidate_ranking_filters():
    ranker = CandidateRanker()
    candidates = [
        {"match_id": "1", "candidate_name": "Candidate A", "overall_score": 75.0, "recommendation": "MATCH", "critical_requirement_missing": False},
        {"match_id": "2", "candidate_name": "Candidate B", "overall_score": 92.0, "recommendation": "STRONG_MATCH", "critical_requirement_missing": False},
        {"match_id": "3", "candidate_name": "Candidate C", "overall_score": 50.0, "recommendation": "WEAK_MATCH", "critical_requirement_missing": True}
    ]
    
    # Filter min_score >= 70
    filtered_score = ranker.rank_candidates(candidates, min_score=70.0)
    assert len(filtered_score) == 2
    assert all(c.overall_score >= 70.0 for c in filtered_score)

    # Filter require_all_mandatory
    filtered_mandatory = ranker.rank_candidates(candidates, require_all_mandatory=True)
    assert len(filtered_mandatory) == 2
    assert not any(c.critical_requirement_missing for c in filtered_mandatory)
