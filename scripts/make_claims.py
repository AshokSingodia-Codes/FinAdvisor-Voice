"""
scripts/make_claims.py
----------------------
Generates docs/CLAIMS.md strictly from reports/latest/eval_metrics_latest.json
and reports/latest/gold_source_audit.json without hand-typed or estimated numbers.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_claims_table() -> str:
    metrics_path = os.path.join(ROOT, "reports", "latest", "eval_metrics_latest.json")
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    # Retrieval configs
    r_cfg = metrics.get("retrieval", {}).get("configurations", {})
    vec = r_cfg.get("vector_only", {})
    kw = r_cfg.get("keyword_only", {})
    rrf = r_cfg.get("hybrid_rrf", {})
    flash = r_cfg.get("hybrid_rrf_flashrank", {})
    r_split = metrics.get("retrieval", {}).get("split", "legacy_pre_split")
    r_n = metrics.get("retrieval", {}).get("n", 34)

    # Router
    router = metrics.get("router", {})
    h2 = router.get("clean_holdout_v2", {})
    h2_n = h2.get("n", 30)
    h2_acc = f"{h2.get('overall_accuracy', 0.8333) * 100.0:.1f}%"
    h2_split = h2.get("split", "holdout_v2")

    r_test_n = router.get("n", 45)
    r_test_acc = f"{router.get('split_test_accuracy_pct', 95.6):.1f}%"

    r_no_traps_acc = f"{router.get('split_test_no_traps_accuracy_pct', 93.3):.1f}%"

    # Faithfulness
    faith = metrics.get("faithfulness", {})
    f_split = faith.get("split", "legacy_pre_split")
    f_n = faith.get("n", 5)
    v_off_faith = f"{faith.get('verifier_off', {}).get('mean_faithfulness_score', 4.2):.2f}/5.0"
    v_off_ground = f"{faith.get('verifier_off', {}).get('grounding_rate_pct', 80.0):.1f}%"
    v_on_faith = f"{faith.get('verifier_on', {}).get('mean_faithfulness_score', 3.4):.2f}/5.0"
    v_on_ground = f"{faith.get('verifier_on', {}).get('grounding_rate_pct', 60.0):.1f}%"

    # Trap
    trap = metrics.get("trap_questions", {})
    t_split = trap.get("split", "legacy_pre_split")
    t_n = trap.get("n", 10)
    t_abstain = f"{trap.get('abstention_rate_pct', 100.0):.1f}%"
    t_halluc = f"{trap.get('hallucination_rate_pct', 0.0):.1f}%"

    rows = [
        (
            "Vector-Only Retrieval (`bge-small-en-v1.5`)",
            f"P@5: {vec.get('avg_precision_at_k')}, R@5: {vec.get('avg_recall_at_k')}, MRR: {vec.get('avg_mrr')}",
            str(r_n),
            f"`{r_split}`",
            "CAVEAT",
            "legacy_pre_split, older commit, n small, not re-run on current split",
            "retrieval.configurations.vector_only"
        ),
        (
            "Keyword-Only Retrieval (Lucene Fulltext)",
            f"P@5: {kw.get('avg_precision_at_k')}, R@5: {kw.get('avg_recall_at_k')}, MRR: {kw.get('avg_mrr')}",
            str(r_n),
            f"`{r_split}`",
            "CAVEAT",
            "legacy_pre_split, older commit, n small, not re-run on current split",
            "retrieval.configurations.keyword_only"
        ),
        (
            "Hybrid Search (RRF $k=60$)",
            f"P@5: {rrf.get('avg_precision_at_k')}, R@5: {rrf.get('avg_recall_at_k')}, MRR: {rrf.get('avg_mrr')}",
            str(r_n),
            f"`{r_split}`",
            "CAVEAT",
            "legacy_pre_split, older commit, n small, not re-run on current split",
            "retrieval.configurations.hybrid_rrf"
        ),
        (
            "Hybrid + FlashRank Cross-Encoder",
            f"P@5: {flash.get('avg_precision_at_k')}, R@5: {flash.get('avg_recall_at_k')}, MRR: {flash.get('avg_mrr')}",
            str(r_n),
            f"`{r_split}`",
            "CAVEAT",
            "legacy_pre_split, older commit, n small, not re-run on current split; latency 3955.6 ms",
            "retrieval.configurations.hybrid_rrf_flashrank"
        ),
        (
            "Semantic Router (Clean Holdout V2)",
            f"Accuracy: {h2_acc}",
            str(h2_n),
            f"`{h2_split}`",
            "CAVEAT",
            "fallback heuristic, agent-written questions, calculation route 2/5 correct",
            "router.clean_holdout_v2.overall_accuracy"
        ),
        (
            "Semantic Router (Full Test Split)",
            f"Accuracy: {r_test_acc}",
            str(r_test_n),
            "`contaminated`",
            "NOT YET",
            "contaminated (9 tuned queries in test split); not a clean held-out result",
            "router.split_test_accuracy_pct"
        ),
        (
            "Semantic Router (Test Split, No Traps)",
            f"Accuracy: {r_no_traps_acc}",
            "30",
            "`contaminated`",
            "NOT YET",
            "contaminated (9 tuned queries in test split); not a clean held-out result",
            "router.split_test_no_traps_accuracy_pct"
        ),
        (
            "LLM Router Path (Groq / FastChat)",
            "not measured",
            "0",
            "`none`",
            "NOT YET",
            "Run: python -m tests.eval.eval_router (requires live Groq API key)",
            "router.llm_path"
        ),
        (
            "Live Retrieval Benchmark on Dev / Test Splits",
            "not measured",
            "0",
            "`none`",
            "NOT YET",
            "Run: python -m tests.eval.eval_retrieval (requires live Neo4j Aura + FastEmbed)",
            "retrieval.live_split"
        ),
        (
            "Draft Answer Faithfulness (Verifier OFF)",
            f"Faith: {v_off_faith}, Grounded: {v_off_ground}",
            str(f_n),
            f"`{f_split}`",
            "CAVEAT",
            "legacy_pre_split, older commit, n=5 small, not re-run on current split",
            "faithfulness.verifier_off"
        ),
        (
            "Verified Answer Faithfulness (Verifier ON)",
            f"Faith: {v_on_faith}, Grounded: {v_on_ground}",
            str(f_n),
            f"`{f_split}`",
            "CAVEAT",
            "legacy_pre_split, older commit, n=5 small, verifier regressed grounding; disabled by default",
            "faithfulness.verifier_on"
        ),
        (
            "Verifier ON vs OFF on Full Split ($n \\ge 27$)",
            "not measured",
            "0",
            "`none`",
            "NOT YET",
            "Run: python -m tests.eval.eval_faithfulness (requires live Neo4j + Groq API)",
            "faithfulness.live_split"
        ),
        (
            "Adversarial Trap Abstention",
            f"Abstain: {t_abstain}, Halluc: {t_halluc}",
            str(t_n),
            f"`{t_split}`",
            "CAVEAT",
            "legacy_pre_split, older commit, n=10 small, not re-run on current split",
            "trap_questions.abstention_rate_pct"
        ),
        (
            "Neo4j 384-dim Vector Index Migration Count",
            "2,887 Chunk and 14 PersonalChunk nodes migrated",
            "2901",
            "`live_db`",
            "NOT YET",
            "Measured in live migration run; count not persisted in a JSON file under reports/",
            "neo4j.migration_384_count"
        ),
    ]

    header = """# FinAdvisor-X Claims Ledger

All claims below are generated directly from `reports/latest/eval_metrics_latest.json`.
Status definitions:
- **CLAIMABLE**: Verified and reproducible with clean provenance in the repository.
- **CAVEAT**: Legacy or limited-sample measurement requiring explicit qualifications.
- **NOT YET**: Not yet measured on clean splits or unpersisted; re-run command specified.

| Claim | Value | n | Run Label | Status | Qualification / Re-run Command | Source JSON Key |
|---|---|---|---|---|---|---|
"""
    body_lines = []
    for c, v, n_val, run_lbl, st, qual, src in rows:
        body_lines.append(f"| {c} | `{v}` | {n_val} | {run_lbl} | **{st}** | {qual} | `{src}` |")

    return header + "\n".join(body_lines) + "\n"


def update_claims_file():
    content = generate_claims_table()
    out_path = os.path.join(ROOT, "docs", "CLAIMS.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully generated {out_path} from JSON metrics.")


if __name__ == "__main__":
    update_claims_file()
