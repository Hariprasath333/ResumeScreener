# Evaluation Methodology & System Benchmarks

## Overview
To ensure system precision, reproducibility, and reliability, Smart Resume Screener features an automated evaluation benchmark framework located in `evaluation/eval_script.py`.

## Evaluation Dimensions

### 1. Skill Extraction Performance
- **Precision**: Ratio of correctly extracted technical skills to total extracted items.
- **Recall**: Ratio of correctly extracted technical skills to ground truth skills present in document.
- **F1 Score**: Harmonic mean of Precision and Recall.

### 2. Candidate Ranking Precision
- **Precision@K**: Percentage of top $K$ ranked candidates that satisfy all mandatory criteria.
- **Mandatory Compliance Rate**: Percentage of candidates accurately penalized when missing mandatory required skills.

### 3. LLM Reliability & JSON Validity
- **JSON Validity Rate**: $100\%$ schema compliance enforced via Pydantic v2 model validation.

## Running the Benchmark
```bash
python evaluation/eval_script.py
```
