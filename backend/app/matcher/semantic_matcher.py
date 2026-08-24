import re
from typing import List, Tuple, Set

STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
    "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
    "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only",
    "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", "should",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then",
    "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why",
    "will", "with", "would", "you", "your", "yours", "yourself", "yourselves"
}

def extract_tokens(text: str) -> Set[str]:
    """Extracts lowercase alphabetic tokens excluding common stopwords."""
    if not text:
        return set()
    words = re.findall(r"[a-zA-Z0-9\+\#\.]+", text.lower())
    return {w for w in words if len(w) > 1 and w not in STOPWORDS}

class SemanticMatcher:
    """Computes robust semantic & domain alignment scores between candidate profile and JD."""

    def _preprocess(self, text: str) -> str:
        if not text:
            return ""
        clean = text.lower()
        clean = re.sub(r"[^\w\s\+\#\.]", " ", clean)
        return re.sub(r"\s+", " ", clean).strip()

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Calculates domain & semantic similarity percentage (0-100) between two text profiles.
        Combines token containment, Jaccard overlap, and keyword density.
        """
        tokens1 = extract_tokens(text1)
        tokens2 = extract_tokens(text2)

        if not tokens1 or not tokens2:
            return 50.0

        intersection = tokens1.intersection(tokens2)
        if not intersection:
            return 20.0

        # Coverage of target requirements (tokens2) in candidate profile (tokens1)
        coverage_ratio = len(intersection) / len(tokens2)
        
        # Jaccard overlap
        jaccard_ratio = len(intersection) / len(tokens1.union(tokens2))

        # Balanced domain similarity score
        raw_score = (coverage_ratio * 0.70 + jaccard_ratio * 0.30) * 100.0
        
        # Scale smoothly: realistic relevant overlap yields 70-95%
        calibrated_score = min(100.0, max(15.0, raw_score * 1.6 + 20.0))
        return round(calibrated_score, 1)

    def compute_responsibility_match(
        self, candidate_responsibilities: List[str], jd_responsibilities: List[str]
    ) -> Tuple[float, List[dict]]:
        """
        Compares candidate work responsibilities with JD responsibilities.
        Returns:
            (overall_score, matched_details_list)
        """
        if not jd_responsibilities:
            return (85.0, [])

        if not candidate_responsibilities:
            return (50.0, [])

        cand_corpus = " ".join(candidate_responsibilities)
        cand_tokens = extract_tokens(cand_corpus)

        scores = []
        details = []

        for req in jd_responsibilities:
            req_tokens = extract_tokens(req)
            if not req_tokens:
                continue

            overlap = req_tokens.intersection(cand_tokens)
            coverage = len(overlap) / len(req_tokens) if req_tokens else 0.0

            # Scale to 0-100
            req_score = min(100.0, max(20.0, coverage * 100.0 + 15.0))
            scores.append(req_score)

            if coverage >= 0.3:
                details.append({
                    "jd_responsibility": req,
                    "overlap_tokens": list(overlap),
                    "coverage_score": round(req_score, 1)
                })

        avg_score = round(sum(scores) / len(scores), 1) if scores else 70.0
        return (min(100.0, max(0.0, avg_score)), details)
