# FinAdvisor-X Empirical Evaluation & Benchmark Report

**Generated:** `2026-10-31 23:45:48 UTC`  
**Git Commit:** `68c0413ad895da0609a622a196d823503c90feb0`  
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

### Retrieval Observations
- **RRF vs Vector-Only Recall:** Recall shifted from 0.6353 to 0.6088 (-4.17% drop).
- **FlashRank Precision vs Latency & MRR Trade-Off:** Adding FlashRank lifted Precision@5 from 0.3941 to 0.4588 (+16.42% gain), but increased latency from 0.90s to 3.96s (a +3.05s / 338% increase) and dropped MRR from 0.676 to 0.574 (a -0.103 / 15.2% drop).

---

## 2. Semantic Intent Router Performance

Evaluated on multi-class intent classification (sample size $n=50$).

- **Overall Routing Accuracy:** `48.0%`
- **Mean Router Latency:** `3.5 ms`

| Intent Class | Support (n) | Precision | Recall | F1-Score |
|---|---|---|---|---|
| `calculation` | 4 | `0.333` | `0.750` | `0.462` |
| `direct_answer` | 0 | `0.000` | `0.000` | `0.000` |
| `hybrid_search` | 44 | `0.950` | `0.432` | `0.594` |
| `live_market_data` | 2 | `0.667` | `1.000` | `0.800` |

### Confusion Matrix
```text
calculation -> calculation: 3
calculation -> hybrid_search: 1
hybrid_search -> calculation: 6
hybrid_search -> direct_answer: 18
hybrid_search -> hybrid_search: 19
hybrid_search -> live_market_data: 1
live_market_data -> live_market_data: 2
```

---

## 3. Answer Faithfulness & Verifier Ablation

Evaluated via LLM auditor measuring factual grounding against retrieved evidence (sample size $n=5$).

| Configuration | n | Mean Faithfulness (1-5 Scale) | Factually Grounded Rate (%) |
|---|---|---|---|
| **Draft Answer (Verifier OFF)** | 5 | `4.2 / 5.0` | `80.0%` |
| **Verified Answer (Verifier ON)** | 5 | `3.4 / 5.0` | `60.0%` |

### Verifier Empirical Findings
- Enabling the Self-RAG verifier resulted in an empirical drop: faithfulness fell from 4.2 to 3.4 (-19.05% drop), and grounding rate dropped from 80.0% to 60.0% (-20.00% pts drop).
- Following these measurements, the verifier is disabled by default (`VERIFIER_ENABLED=False`) in `config/settings.py`.

---

## 4. Hallucination Resistance & Adversarial Trap Benchmark

Evaluated on adversarial out-of-corpus queries (sample size $n=10$).

- **Safe Abstention Rate:** `100.0%`
- **Hallucination Incident Rate:** `0.0%`
