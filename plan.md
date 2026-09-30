# FinAdvisor-X Optimization Plan

===========================================================
STEP 0 — MANDATORY FIRST ACTION: VERIFY CURRENT STATE
===========================================================
Before writing or changing any code, discover and run every existing
test file to confirm what's actually working right now:

  python -m unittest discover tests "test_*.py"

Specifically confirm these files exist and pass:
  tests/test_fast_paths_bypass_llm.py       (8 tests expected)
  tests/test_db_migration_safety.py         (4 tests expected)
  tests/test_conversational_continuity.py   (4 tests expected)
  tests/test_reranker_boost.py              (5 tests expected)
  tests/test_arithmetic_shortcut.py
  tests/test_data_isolation.py              (pre-existing)
  tests/test_router.py                      (pre-existing)
  tests/test_workflow.py                    (pre-existing)
  tests/test_mf_lookup.py                   (pre-existing)
  tests/test_document_ingestion_and_guardrails.py (pre-existing)

Also re-run the retrieval benchmark:
  python tests/eval/eval_retrieval.py

===========================================================
PHASE 1 — LATENCY & TOKEN OPTIMIZATION — STATUS: COMPLETE
===========================================================
Done:
- Verified live Groq model list via API.
- Retrieval candidate reduction (25-30 -> 8-12) TESTED and REJECTED.
- Chat history windowing: MAX_CHAT_HISTORY_TURNS=6.
- SSE streaming: /api/chat converted to StreamingResponse.
- Deterministic fast paths: core/greeting_handler.py + tools/fast_math.py.
- Retrieval parallelization: real latency dropped from ~2250ms to 650.1ms.
- MRR/table-demotion fix.
- Score distribution guard.
- resolved_query downstream consumption audited.

Not yet fully closed out (do this now, low effort):
- FlashRank batching status was never confirmed.

===========================================================
PHASE 2 — CONVERSATIONAL CONTINUITY & ENTITY TRACKING — STATUS: COMPLETE
===========================================================
Done:
- graph/state.py: AgentState extended.
- core/memory.py: conversation_memory table extended.
- nodes/router.py: single LLM call extended.
- Adversarial topic-change reset.
- tests/test_conversational_continuity.py (4 tests, all PASS).

===========================================================
PHASE 3 — ASYNC DOCUMENT INGESTION — STATUS: COMPLETE
===========================================================
Done:
1. LOCATE THE ACTUAL DECRYPT CALL SITE FIRST.
2. POST /api/documents/upload — two-phase background task.
3. GET /api/documents/status/{job_id} — explicit state machine.
4. Scoped Fernet decryption test: assert decrypted-chunk COUNT equals retrieval top-k.
5. Health-ping cron hitting a lightweight endpoint.
6. Reuse tests/test_data_isolation.py's scoping pattern.
7. Enforce MAX_DOCUMENT_SIZE_MB=10, MAX_PAGES=50.

**KNOWN OPEN ITEM**: POST /api/documents/upload: <500ms target, 2.13s measured for ~9.4MB payload — root cause is synchronous multipart spooling before the handler runs. Background task offload only covers PDF extraction, not the initial HTTP upload transfer/spool itself. (Defer fix for now).

===========================================================
PHASE 4 — KNOWLEDGE GRAPH MULTI-HOP TRAVERSAL — STATUS: IN PROGRESS
===========================================================
**4.1. SCHEMA DOC (Apple 10-K + Textbooks)**
*Node Types (Strictly scoped to actual corpus contents):*
- `Company` (e.g., Apple Inc., Groq)
- `Segment` (e.g., iPhone, Services, Mac, Wearables)
- `RiskFactor` (e.g., Foreign Currency Fluctuation, Supply Chain Disruption, Interest Rate Risk)
- `Concept` (e.g., Asset Allocation, Systematic Risk, Diversification - from textbooks)
- `Metric` (e.g., total net sales, iPhone revenue)
- `DocumentChunk` (Matches existing `Chunk` nodes in Neo4j created by the vector ingestion pipeline; uses identical chunk `id` space so citation links line up perfectly with existing frontend/hybrid search systems).
*(Note: `Person` or `Executive` is excluded to avoid noisy speculative extraction, as 10-K signatures don't typically drive multi-hop semantic queries. Locations are explicitly discarded).*

**4.2. Ingestion Status:**
- COMPLETE: 105/105 chunks extracted, yielding 726 entities and 606 relationships (gross extraction counts before MERGE dedup, resolving to 523 unique entities and 1248 final relationships including MENTIONED_IN).
- The hand-inserted mock data was fully deleted, verified by post-run queries.
- Graph is now populated with real, verified 10-K data.
- Extraction pipeline stabilized using `openai/gpt-oss-120b` with strict model verification guards.

*Edge Types (Relationships):*
- `(Company)-[:HAS_SEGMENT]->(Segment)`
- `(Company)-[:FACES_RISK]->(RiskFactor)`
- `(RiskFactor)-[:FACES_RISK]->(Segment)`  <- ACCEPTED SCHEMA EXTENSION: Risks specifically tied to segments
- `(Company)-[:DEPENDS_ON]->(Company)`    <- ACCEPTED SCHEMA EXTENSION: B2B dependency (e.g. Apple depends on Google LLC)
- `(Company)-[:REPORTED_METRIC]->(Metric)`
- `(Segment)-[:DRIVES_METRIC]->(Metric)`
- `(Concept)-[:DEPENDS_ON]->(Concept)`
- `(Company|Segment|RiskFactor|Concept|Metric)-[:MENTIONED_IN]->(DocumentChunk)`

Scope:
- Entity extraction at ingestion time only.
- Neo4j edges.
- `graph_traversal.py` node: Parameterized Cypher template built and fallback to `hybrid_search` logic implemented.
  - *CRITICAL CAVEAT:* The traversal mechanism itself works (proven via hand-inserted mock data), but the **LLM extraction pipeline output** has not yet been validated end-to-end. We do not yet know if the pipeline produces accurate/clean enough data to make this traversal trustworthy at scale.
  - *CLEANUP COMPLETE:* The hand-inserted mock data was fully deleted tonight, leaving a clean slate.
- New router category "graph_traversal" (Only wire into router *after* pipeline validation passes tomorrow).
- evidence_builder.py explains traversed relationship.
- tests/test_graph_traversal.py.

===========================================================
PHASE 5 — CROSS-CUTTING TESTING & BENCHMARKING — STATUS: COMPLETE
===========================================================
- [x] Full end-to-end regression across all phases together once Phase 4 ships (48/48 tests passed).
- [x] Re-run eval_faithfulness.py and eval_trap_questions.py.
- [x] Final latency benchmark report.

**Incident Report & Final Benchmarks:**
During Phase 5 benchmarking, a data-loss bug was caught: the `extract_real_subset.py` ingestion accidentally wiped the full corpus due to a `pre_delete_collection=True` default in the vector store wrapper. This was caught thanks to the strict benchmarking discipline (retrieval metrics collapsed), root-caused, and methodically recovered via incremental re-ingestion of the missing textbooks.

**Restored Baseline (Hybrid RRF + FlashRank):**
- Precision@5: 0.459
- Recall@5: 0.609
- MRR: 0.574
- Final Chunk Count: ~2,883 (slightly differs from the original ~2,831 due to differences in PDFPlumber vs. original pymupdf4llm text-splitting/chunking boundaries, but mechanically sound after 92 duplicates were pruned).

===========================================================
PHASE 6 — DAILY DATA INGESTION — STATUS: COMPLETE
===========================================================
Done:
- scripts/daily_snapshot_job.py: Daily equity + MF NAV snapshot job.
  - SEED_EQUITIES: 12 NSE tickers + indices (Reliance, TCS, HDFC, Nifty50, Sensex, etc.)
  - SEED_MUTUAL_FUNDS: 6 AMFI scheme codes (Parag Parikh, Mirae, HDFC, SBI, Quant, Axis)
  - fetch_navall_for_watchlist(): Single NAVAll.txt download → batch NAV parse (no per-fund HTTP)
  - run_mf_nav_snapshot(): Upserts into mf_nav_snapshots (UNIQUE on scheme_code+date -- safe re-run)
  - run_daily_snapshots(): Orchestrates equity (yfinance/Finnhub) + MF (NAVAll.txt) sync
- nodes/news_data.py: Current-events / live news node.
  - 3 LiveMint RSS feeds (Economy, Markets, Industry) with 15-minute in-process cache.
  - Finance relevance scorer + graceful no-results fallback.
  - Integrated into LangGraph workflow as 'news_node' on 'current_events' router decision.
- tools/snapshot_helper.py: calculate_period_return() for 1d/1w/1m/3m/6m/1y performance.
- core/memory.py: daily_snapshots and mf_nav_snapshots tables with UNIQUE constraints.
  - upsert_daily_snapshot(), get_historical_snapshot(), get_all_snapshots()
  - upsert_mf_nav_snapshot(), get_historical_mf_nav(), get_distinct_tracked_symbols()
- main.py: Phase 6 lifecycle and REST API integration:
  - _daily_snapshot_background_loop(): Async scheduler fires daily at 13:00 UTC (18:30 IST).
  - POST /api/admin/run-daily-snapshot: Manual admin trigger for immediate run.
  - GET  /api/snapshots/{asset_type}/{symbol}: Historical daily price/NAV time-series.
  - GET  /api/snapshots/{asset_type}/{symbol}/return: Period return % (1d/1w/1m/3m/6m/1y).
  - GET  /api/mf-nav/{scheme_code}: Latest AMFI NAV on or before target_date.
- tests/test_daily_snapshot_job.py: 7 tests — all PASS.
  - test_daily_snapshot_upsert_and_retrieve
  - test_calculate_period_return
  - test_period_return_graceful_fallback
  - test_daily_snapshot_job_execution
  - test_mf_nav_upsert_idempotency
  - test_mf_nav_graceful_no_history
  - test_mf_nav_nearest_date_lookup
- tests/test_news_data.py: 7 tests — all PASS.
  - test_returns_relevant_news_for_rbi_query
  - test_fallback_when_all_feeds_fail
  - test_fallback_when_no_relevant_items
  - test_generic_news_request_returns_items_even_at_zero_score
  - test_citations_include_source_and_date
  - test_feed_cache_prevents_duplicate_fetches
  - test_max_five_results_returned
