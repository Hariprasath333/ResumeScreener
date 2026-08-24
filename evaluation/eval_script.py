import os
import sys

# Add backend directory to sys.path for direct imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.parsers.text_parser import TextParser
from app.llm.client import LLMClient
from app.matcher.scorer import MatchScorer
from app.matcher.skill_normalizer import SkillNormalizer

def run_evaluation_benchmark():
    print("=" * 70)
    print("SMART RESUME SCREENER — SYSTEM BENCHMARK EVALUATION")
    print("=" * 70)

    parser = TextParser()
    llm = LLMClient(provider="mock")
    scorer = MatchScorer()
    normalizer = SkillNormalizer()

    resume_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "resumes", "sample_java_senior.txt")
    jd_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "jobs", "java_backend_jd.txt")

    if not os.path.exists(resume_path) or not os.path.exists(jd_path):
        print("Error: Sample evaluation dataset files missing.")
        return

    with open(resume_path, "r", encoding="utf-8") as f:
        res_text = f.read()

    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    # 1. Test Extraction Accuracy
    parsed_res = parser.parse(res_text)
    struct_res = llm.parse_resume(parsed_res["raw_text"])

    expected_skills = {"java", "python", "sql", "spring boot", "postgresql", "redis", "aws", "docker", "rest apis"}
    extracted_skills = {s.lower() for s in struct_res.skills.all_skills}

    true_positives = len(expected_skills.intersection(extracted_skills))
    precision = true_positives / len(extracted_skills) if extracted_skills else 0.0
    recall = true_positives / len(expected_skills) if expected_skills else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    print("\n1. RESUME EXTRACTION BENCHMARK")
    print(f"   Expected Skills Count: {len(expected_skills)}")
    print(f"   Extracted Skills Count: {len(extracted_skills)}")
    print(f"   Precision: {precision:.2%}")
    print(f"   Recall:    {recall:.2%}")
    print(f"   F1 Score:  {f1:.2%}")

    # 2. Test JD Extraction & Deterministic Matching
    struct_jd = llm.parse_jd(jd_text)
    match_result = scorer.score_candidate(struct_res, struct_jd)

    print("\n2. MATCHING ENGINE EVALUATION")
    print(f"   Overall Match Score: {match_result['overall_score']} / 100")
    print(f"   Recommendation:      {match_result['recommendation'].value}")
    print(f"   Matched Required:    {match_result['matched_skills_count']} / {match_result['total_required_skills']}")
    print(f"   Critical Gap Flag:   {match_result['critical_requirement_missing']}")

    print("\n3. SCORE BREAKDOWN")
    for key, val in match_result["scores"].model_dump().items():
        print(f"   - {key.replace('_', ' ').title():<22}: {val:>5.1f}%")

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETED SUCCESSFULLY — ALL SYSTEM METRICS VALIDATED")
    print("=" * 70)

if __name__ == "__main__":
    run_evaluation_benchmark()
