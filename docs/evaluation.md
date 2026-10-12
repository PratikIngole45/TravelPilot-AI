# TravelPilot AI — Evaluation Results

> Generated from automated test suite (30 test scenarios across retrieval and deterministic itinerary planning).

## 1. Executive Summary

| Target Metric | Target Criterion | Measured Result | Status |
| :--- | :--- | :--- | :--- |
| **Deterministic Schema Validity** | 100% | **100.0%** | **PASSED** |
| **Code-Calculated Math (No LLM Arithmetics)** | 100% | **100.0%** | **PASSED** |
| **Constraint Pass Rate** | >= 90% | **100.0%** | **PASSED** |
| **Retrieval Recall@3** | High Grounding | **100.0%** | **PASSED** |
| **Mean Reciprocal Rank (MRR)** | > 0.8 | **1.000** | **PASSED** |
| **Planning Latency** | < 100ms | **0.49 ms** | **PASSED** |

## 2. Retrieval Evaluation Breakdown
- **Model:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Vector Index:** FAISS `IndexFlatIP` (Cosine similarity on L2-normalized embeddings)
- **Labelled Queries Evaluated:** 8
- **Mean Recall@3:** 100.0%
- **Mean Precision@3:** 83.3%
- **MRR:** 1.000

## 3. Itinerary Generation & Constraint Verification Breakdown
- **Test Scenarios Evaluated:** 22
- **Schema Validity:** 100.0%
- **Deterministic Arithmetic Accuracy:** 100.0%
- **Constraint Satisfaction Rate:** 100.0%
- **Average Execution Latency:** 0.49 ms
