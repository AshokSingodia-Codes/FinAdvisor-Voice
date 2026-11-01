# FinAdvisor-X Empirical Evaluation & Benchmark Report

**Generated:** `2026-11-01 00:04:30 UTC`  
**Git Commit:** `eda0d2f`  
**Embedding Model:** `BAAI/bge-small-en-v1.5` (384-dim, FastEmbed)  
**Architecture:** Hybrid RAG: Neo4j vector + Lucene fulltext, RRF fusion, FlashRank rerank  

---

## 1. Retrieval & Reranking Benchmark

Evaluated on in-corpus SEC 10-K filings and corporate finance textbook queries (sample size $n=34$).

| Pipeline Stage | n | Precision@5 | Recall@5 | MRR | Latency |
|---|---|---|---|---|---|
| **1. Vector-Only (FastEmbed bge-small)** | 34 | `0.3882` | `0.6353` | `0.6529` | `3043.1 ms` |
| **2. Keyword-Only (Lucene Fulltext)** | 34 | `0.4412` | `0.598` | `0.6382` | `976.5 ms` |
| **3. Hybrid Search (RRF Fusion, k=60)** | 34 | `0.3941` | `0.6088` | `0.6765` | `903.1 ms` |
| **4. Hybrid + FlashRank Cross-Encoder** | 34 | `0.4588` | `0.6088` | `0.5735` | `3955.6 ms` |

### Retrieval Deltas (Computed from Unrounded JSON Values)
- **Hybrid RRF vs Vector-Only Recall:** abs change = `-0.0265`, rel change = `-4.17%` (-0.0265 (-4.17%) drop).
- **Hybrid RRF vs Vector-Only MRR:** abs change = `+0.0236`, rel change = `+3.61%` (+0.0236 (+3.61%) gain).
- **FlashRank Precision vs Hybrid:** abs change = `+0.0647`, rel change = `+16.42%` (+0.0647 (+16.42%) gain).
- **FlashRank MRR vs Hybrid:** abs change = `-0.1030`, rel change = `-15.23%` (-0.1030 (-15.23%) drop).
- **FlashRank Latency vs Hybrid:** abs change = `+3.0525s`, rel change = `+338.00%` (+3.0525s (+338.00%) gain).

---

## 2. Semantic Intent Router Performance

Evaluated on multi-class intent classification (sample size $n=45$, path: `fallback_heuristic`).

- **Overall Routing Accuracy:** `95.6%`
- **Mean Router Latency:** `434.4 ms` (measured on `fallback_heuristic` path)

| Intent Class | Support (n) | Precision | Recall | F1-Score |
|---|---|---|---|---|
| not measured | not measured | not measured | not measured | not measured |

### Confusion Matrix
```text
hybrid_search -> hybrid_search: 41
hybrid_search -> live_market_data: 1
calculation -> hybrid_search: 1
calculation -> calculation: 1
live_market_data -> live_market_data: 1
```

---

## 3. Answer Faithfulness & Verifier Ablation

Evaluated via LLM auditor measuring factual grounding against retrieved evidence (sample size $n=5$).

| Configuration | n | Mean Faithfulness (1-5 Scale) | Factually Grounded Rate (%) |
|---|---|---|---|
| **Draft Answer (Verifier OFF)** | 5 | `4.20 / 5.0` | `80.0%` |
| **Verified Answer (Verifier ON)** | 5 | `3.40 / 5.0` | `60.0%` |

### Verifier Empirical Deltas
- **Faithfulness Score:** abs change = `-0.80`, rel change = `-19.05%` (-0.8000 (-19.05%) drop).
- **Grounded Rate:** abs change = `-20.00% pts` (drop).
- **Decision:** On the recorded n=5 run, faithfulness went 4.2 to 3.4 and grounded rate 80% to 60%. n=5 is too small to conclude. Disabled by default pending re-measurement on >=30 questions. Run: `python scripts/run_all_evals.py --split test`.

---

## 4. Hallucination Resistance & Adversarial Trap Benchmark

Evaluated on adversarial out-of-corpus queries (sample size $n=10$).

- **Safe Abstention Rate:** `100.0%`
- **Hallucination Incident Rate:** `0.0%`
