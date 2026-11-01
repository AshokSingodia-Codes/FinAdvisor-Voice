# FinAdvisor-X — Master Evaluation Report

> **Generated:** 2026-09-30 18:58 UTC  
> **Suite Status:** `HAS_FAILURES`  
> **Total Tests:** `80/82` passed (97.6%)

---

## 1. Unit Test Suite Results

| Phase / Module | Tests | Passed | Failed | Status | Duration |
|---|---|---|---|---|---|
| Phase 1 — Latency & Token Optimisation | 0 | 0 | 0 | ❌ TIMEOUT | 300s |
| Phase 2 — Conversational Continuity | 8 | 8 | 0 | ✅ PASS | 141.8s |
| Phase 3 — Async Document Ingestion | 37 | 37 | 0 | ✅ PASS | 39.6s |
| Phase 4 — Knowledge Graph | 1 | 1 | 0 | ✅ PASS | 15.9s |
| Phase 5 — Cross-Cutting Testing | 14 | 13 | 1 | ❌ FAIL | 115.4s |
| Phase 6 — Daily Data Ingestion | 14 | 13 | 1 | ❌ FAIL | 91.2s |
| Auth & Security | 0 | 0 | 0 | ❌ TIMEOUT | 300s |
| Market Data | 8 | 8 | 0 | ✅ PASS | 55.5s |

**Grand Total: 80/82 tests passed (97.6%)**

---

## 2. Retrieval Benchmark

| Configuration | Precision@5 | Recall@5 | MRR | Latency |
|---|---|---|---|---|
| vector_only | `0.3882` | `0.6353` | `0.6529` | `3.0431s` |
| keyword_only | `0.4412` | `0.598` | `0.6382` | `0.9765s` |
| hybrid_rrf | `0.3941` | `0.6088` | `0.6765` | `0.9031s` |
| hybrid_rrf_flashrank | `0.4588` | `0.6088` | `0.5735` | `3.9556s` |

---

## 3. Router Accuracy

- **Total:** 50
- **Correct:** N/A
- **Accuracy:** `48.0%`

---

## 4. Hallucination & Trap Resistance

- **Trap Questions:** N/A
- **Safe Abstentions:** N/A
- **Hallucinated:** N/A
- **Safe Abstention Rate:** `N/A%`

---

## 5. Answer Faithfulness (Self-RAG)

- **Mean Draft Score:** `N/A / 5.0`
- **Mean Verified Score:** `N/A / 5.0`
- **Grounded Rate:** `N/A%`

---

## 6. Architecture Feature Coverage

| Feature | Status |
|---|---|
| Hybrid Graph-RAG (BM25 + Dense Vector RRF) | ✅ Active |
| FlashRank Neural Cross-Encoder Reranker | ✅ Active |
| LangGraph Multi-Agent Orchestration | ✅ Active |
| Self-RAG Hallucination Verifier | ✅ Active |
| Dual-Tier LLM (Llama-70B / GPT-OSS-120B) | ✅ Active |
| Deterministic Fast-Math Engine (<1ms) | ✅ Active |
| Greeting Gate (<1ms bypass) | ✅ Active |
| Conversational Entity Tracking & Pronoun Resolution | ✅ Active |
| Async Document Upload + Background Ingestion | ✅ Active |
| Token-Efficient PDF/Table Compressor | ✅ Active |
| 3-Field Personal Doc Isolation | ✅ Active |
| Knowledge Graph Multi-Hop Traversal | ✅ Active |
| MF Deterministic Lookup (<2ms) | ✅ Active |
| Monthly Regulatory Watchdog | ✅ Active |
| Daily Equity + NAV Snapshot Scheduler | ✅ Active (Phase 6) |
| Live News RSS Node (15min cache) | ✅ Active (Phase 6) |
| Historical Return API (1d/1w/1m/3m/6m/1y) | ✅ Active (Phase 6) |
| SSE Streaming Chat | ✅ Active |
| JWT Auth + OTP Email Verification | ✅ Active |
| Sliding-Window Rate Limiter | ✅ Active |
| React Vite Frontend (TTS, Action Chips, Copy) | ✅ Active |
| FastAPI Lifespan (migrated from on_event) | ✅ Active |

---

## ⚠️ 7. Failure Details

### Phase 5 — Cross-Cutting Testing

```
    ^^^^^^^^^^^^^^^^^^^^
E   AssertionError: assert '|' in '**Insufficient verified evidence is available to provide a comparison between HDFC Bank and ICICI Bank.**  \n\n[Obtain recent financial statements or market data for both banks]'
---------------------------- Captured stdout call -----------------------------
[cache] MISS key=089331044e05…
---NODE: ROUTER---
Decision: decompose, Depth: quick, Topic: Bank comparison, Entities: {'company': 'HDFC Bank, ICICI Bank'}
---NODE: DECOMPOSITION---
Decomposed into 3 queries: ['HDFC Bank financial performance and key metrics', 'ICICI Bank financial performance and key metrics', 'HDFC Bank vs ICICI Bank comparison']
---NODE: RETRIEVER---
  [Mode: SHARED CORPUS]
  Retrieving for: HDFC Bank financial performance and key metrics
  Retrieving for: ICICI Bank financial performance and key metrics
  Retrieving for: HDFC Bank vs ICICI Bank comparison
---NODE: EVIDENCE BUILDER---
  [Evidence Builder: SYNTHESIS] depth='quick', doc=False (4 chunks bounded)
[DEBUG] ---NODE: VERIFIER RUNNING (verifier_enabled=True)---
[cache] SET  key=089331044e05…
============================== warnings summary ===============================
tests/test_indian_context.py::test_indian_stock_query
tests/test_indian_context.py::test_student_advisor_query
tests/test_indian_context.py::test_company_comparison
  C:\Users\srcsi\AppData\Local\Programs\Python\Python312\Lib\site-packages\jose\jwt.py:311: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    now = timegm(datetime.utcnow().utctimetuple())

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_indian_context.py::test_company_comparison - AssertionError...
============ 1 failed, 13 passed, 3 warnings in 102.79s (0:01:42) =============
C:\Users\srcsi\AppData\Local\Programs\Python\Python312\Lib\site-packages\requests\__init__.py:113: RequestsDependencyWarning: urllib3 (2.2.1) or chardet (7.4.3)/charset_normalizer (3.3.2) doesn't match a supported version!
  warnings.warn(
```

### Phase 6 — Daily Data Ingestion

```
============================= test session starts =============================
platform win32 -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: E:\finaceadviser\reference_projects\Hybrid-Graph-RAG-Financial-Analyser-main
configfile: pytest.ini
plugins: anyio-4.12.1, langsmith-0.12.6, asyncio-1.4.0, mock-3.15.1, typeguard-4.4.4
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 14 items

tests\test_daily_snapshot_job.py ......F                                 [ 50%]
tests\test_news_data.py .......                                          [100%]

================================== FAILURES ===================================
_______________________ test_mf_nav_nearest_date_lookup _______________________
tests\test_daily_snapshot_job.py:178: in test_mf_nav_nearest_date_lookup
    assert rec["nav"] == 200.0, (
E   AssertionError: Expected nav from 2026-09-20 (nearest prior to 2026-09-23), got nav=210.0 from 2026-09-23
E   assert 210.0 == 200.0
=========================== short test summary info ===========================
FAILED tests/test_daily_snapshot_job.py::test_mf_nav_nearest_date_lookup - As...
=================== 1 failed, 13 passed in 73.73s (0:01:13) ===================
C:\Users\srcsi\AppData\Local\Programs\Python\Python312\Lib\site-packages\requests\__init__.py:113: RequestsDependencyWarning: urllib3 (2.2.1) or chardet (7.4.3)/charset_normalizer (3.3.2) doesn't match a supported version!
  warnings.warn(
```


---
*Report generated at 2026-09-30 18:58 UTC*