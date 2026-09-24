# FinAdvisor-X Comprehensive System Health, Diagnostic & Improvement Plan

**Date:** September 24, 2026  
**Status:** In Progress — Upgrading Keyword Retrieval & Self-RAG Verifier  

---

## 1. Executive Diagnostic & Real Condition of the Project

FinAdvisor-X is an enterprise-grade agentic financial analysis system combining:
1. **Neo4j Graph Database**: Entity relationships + Vector & Full-Text indexes.
2. **Dense Vector Retrieval**: Sentence-Transformers / FastEmbed embeddings.
3. **FlashRank Cross-Encoder**: Dynamic candidate re-ranking.
4. **LangGraph Agentic Orchestration**: Multi-path routing (Decompose, Hybrid Search, Financial Tables, Math Calculation, Live Market Data, Direct Chat).
5. **Self-RAG Fact-Checking Loop**: Automated verification against raw context.

### Overall Scorecard

| Component | Benchmark Metric | Current Score | Real Health Assessment |
|---|---|---|---|
| **Vector Retrieval** | Recall@5 | **0.651** (8.5/10) | Fast dense search (~698ms) reliably finding candidate chunks. |
| **FlashRank Reranker** | Precision@5 Lift | **+5.16%** (9.0/10) | Highly effective at re-ordering table lines to top-1 rank. |
| **Hallucination Defense** | Trap Abstention Rate | **100.0%** (9.5/10) | Strong guardrail against unindexed and fictitious companies. |
| **Live Market Data** | F1-Score | **1.000** (9.0/10) | Real-time ticker and price lookups work seamlessly. |
| **Keyword / Graph Search** | Precision@5 | **0.000** (3.0/10) | **Defect Identified:** Was returning relationship triples instead of querying the Neo4j `keyword_markdown` fulltext index. |
| **Semantic Intent Router** | Overall Accuracy | **52.0%** (6.0/10) | Routes math and tickers well; required prompt refinement to separate formula definitions from calculations. |
| **Self-RAG Verifier** | Grounding Rate | **0.0% - 10.0%** (5.0/10) | **Defect Identified:** Rule 4 penalized valid safe abstentions, and strict auditor rules rejected hypothetical math examples. |

---

## 2. Root Cause Analysis of Weak Areas

### A. Why Keyword / Graph Retrieval Scored Weakly (3.0 / 10)
* **Problem**: In `nodes/retriever.py`, `structured_retriever` called an LLM entity extraction chain and queried Neo4j for relationship edges (`node - TYPE -> neighbor`). It returned text strings like `"Apple - HAS_REPORT -> Form10K"`, which contained no paragraph or table content.
* **Solution**: Query the native Neo4j Lucene fulltext index `keyword_markdown` (`CALL db.index.fulltext.queryNodes('keyword_markdown', $query)`), which indexes all 2,831 markdown text chunks with BM25 token scoring.

### B. Why Self-RAG Verifier Over-Penalized Responses (5.0 / 10)
* **Problem 1**: The system prompt instructed the verifier: *"If the draft answer explicitly says it does not have enough information, return is_supported=False."* This caused valid, safe abstentions on unindexed queries to fail verification and loop infinitely.
* **Problem 2**: The numerical auditor required every single number in the draft to exist in the context. For educational planning (e.g. SIP examples), hypothetical numbers (e.g. "₹5,000 monthly SIP") were rejected.
* **Solution**: Calibrate the verifier to validate company financial claims strictly against 10-Ks, while allowing verified safe abstentions and mathematically consistent hypothetical examples.

---

## 3. Implementation Plan & Progress

- [x] Step 1: Benchmark and compile baseline reports across all 5 evaluation dimensions.
- [x] Step 2: Fix Semantic Intent Router formula definition misrouting.
- [x] Step 3: Diagnostic report compilation (`reports/SYSTEM_HEALTH_AND_IMPROVEMENT_PLAN.md`).
- [ ] Step 4: Upgrade `nodes/retriever.py` with Lucene Full-Text BM25 Search + Graph traversal.
- [ ] Step 5: Calibrate `nodes/verifier.py` (Self-RAG Verifier prompt & logic).
- [ ] Step 6: Validate improvements with automated unit and regression tests.
