# FinAdvisor-X Claims Ledger

All claims below are generated directly from `reports/latest/eval_metrics_latest.json`.
Status definitions:
- **CLAIMABLE**: Verified and reproducible with clean provenance in the repository.
- **CAVEAT**: Legacy or limited-sample measurement requiring explicit qualifications.
- **NOT YET**: Not yet measured on clean splits or unpersisted; re-run command specified.

| Claim | Value | n | Run Label | Status | Qualification / Re-run Command | Source JSON Key |
|---|---|---|---|---|---|---|
| Vector-Only Retrieval (`bge-small-en-v1.5`) | `P@5: 0.3882, R@5: 0.6353, MRR: 0.6529` | 34 | `legacy_pre_split` | **CAVEAT** | legacy_pre_split, older commit, n small, not re-run on current split | `retrieval.configurations.vector_only` |
| Keyword-Only Retrieval (Lucene Fulltext) | `P@5: 0.4412, R@5: 0.598, MRR: 0.6382` | 34 | `legacy_pre_split` | **CAVEAT** | legacy_pre_split, older commit, n small, not re-run on current split | `retrieval.configurations.keyword_only` |
| Hybrid Search (RRF $k=60$) | `P@5: 0.3941, R@5: 0.6088, MRR: 0.6765` | 34 | `legacy_pre_split` | **CAVEAT** | legacy_pre_split, older commit, n small, not re-run on current split | `retrieval.configurations.hybrid_rrf` |
| Hybrid + FlashRank Cross-Encoder | `P@5: 0.4588, R@5: 0.6088, MRR: 0.5735` | 34 | `legacy_pre_split` | **CAVEAT** | legacy_pre_split, older commit, n small, not re-run on current split; latency 3955.6 ms | `retrieval.configurations.hybrid_rrf_flashrank` |
| Semantic Router (Clean Holdout V2) | `Accuracy: 83.3%` | 30 | `holdout_v2` | **CAVEAT** | fallback heuristic, agent-written questions, calculation route 2/5 correct | `router.clean_holdout_v2.overall_accuracy` |
| Semantic Router (Full Test Split) | `Accuracy: 95.6%` | 45 | `contaminated` | **NOT YET** | contaminated (9 tuned queries in test split); not a clean held-out result | `router.split_test_accuracy_pct` |
| Semantic Router (Test Split, No Traps) | `Accuracy: 93.3%` | 30 | `contaminated` | **NOT YET** | contaminated (9 tuned queries in test split); not a clean held-out result | `router.split_test_no_traps_accuracy_pct` |
| LLM Router Path (Groq / FastChat) | `not measured` | 0 | `none` | **NOT YET** | Run: python -m tests.eval.eval_router (requires live Groq API key) | `router.llm_path` |
| Live Retrieval Benchmark on Dev / Test Splits | `not measured` | 0 | `none` | **NOT YET** | Run: python -m tests.eval.eval_retrieval (requires live Neo4j Aura + FastEmbed) | `retrieval.live_split` |
| Draft Answer Faithfulness (Verifier OFF) | `Faith: 4.20/5.0, Grounded: 80.0%` | 5 | `legacy_pre_split` | **CAVEAT** | legacy_pre_split, older commit, n=5 small, not re-run on current split | `faithfulness.verifier_off` |
| Verified Answer Faithfulness (Verifier ON) | `Faith: 3.40/5.0, Grounded: 60.0%` | 5 | `legacy_pre_split` | **CAVEAT** | legacy_pre_split, older commit, n=5 small, verifier regressed grounding; disabled by default | `faithfulness.verifier_on` |
| Verifier ON vs OFF on Full Split ($n \ge 27$) | `not measured` | 0 | `none` | **NOT YET** | Run: python -m tests.eval.eval_faithfulness (requires live Neo4j + Groq API) | `faithfulness.live_split` |
| Adversarial Trap Abstention | `Abstain: 100.0%, Halluc: 0.0%` | 10 | `legacy_pre_split` | **CAVEAT** | legacy_pre_split, older commit, n=10 small, not re-run on current split | `trap_questions.abstention_rate_pct` |
| Neo4j 384-dim Vector Index Migration Count | `2,887 Chunk and 14 PersonalChunk nodes migrated` | 2901 | `live_db` | **NOT YET** | Measured in live migration run; count not persisted in a JSON file under reports/ | `neo4j.migration_384_count` |
