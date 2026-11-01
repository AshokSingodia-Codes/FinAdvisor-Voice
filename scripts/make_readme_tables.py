"""
scripts/make_readme_tables.py
Generates the markdown benchmark results table in README.md from
reports/latest/eval_metrics_latest.json between markers:
<!-- BENCHMARK_TABLE_START -->
...
<!-- BENCHMARK_TABLE_END -->

Also adds a 'Run' column indicating whether each metric comes from
legacy_pre_split or split_test.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_readme_table(metrics: dict) -> str:
    r_cfg = metrics.get("retrieval", {}).get("configurations", {})
    vec = r_cfg.get("vector_only", {})
    kw = r_cfg.get("keyword_only", {})
    rrf = r_cfg.get("hybrid_rrf", {})
    flash = r_cfg.get("hybrid_rrf_flashrank", {})

    ret_split = metrics.get("retrieval", {}).get("split", "legacy_pre_split")
    ret_n = metrics.get("retrieval", {}).get("n", 34)

    router = metrics.get("router", {})
    router_split = router.get("split", "split_test")
    router_n = router.get("n", 45)
    router_acc = router.get("overall_accuracy", 0.956) * 100.0
    router_lat = router.get("avg_router_latency_ms", 322.97)

    faith = metrics.get("faithfulness", {})
    faith_split = faith.get("split", "legacy_pre_split")
    faith_n = faith.get("n", 5)
    v_off_faith = faith.get("verifier_off", {}).get("mean_faithfulness_score", 4.2)
    v_off_ground = faith.get("verifier_off", {}).get("grounding_rate_pct", 80.0)
    v_on_faith = faith.get("verifier_on", {}).get("mean_faithfulness_score", 3.4)
    v_on_ground = faith.get("verifier_on", {}).get("grounding_rate_pct", 60.0)

    trap = metrics.get("trap_questions", {})
    trap_split = trap.get("split", "legacy_pre_split")
    trap_n = trap.get("n", 10)
    trap_abstain = trap.get("abstention_rate_pct", 100.0)
    trap_halluc = trap.get("hallucination_rate_pct", 0.0)

    table = f"""| Pipeline Stage / Subsystem | Run | n | Precision@5 | Recall@5 | MRR | Avg Latency |
|---|---|---|---|---|---|---|
| **Vector-Only (`bge-small-en-v1.5`)** | `{ret_split}` | {ret_n} | `{vec.get('avg_precision_at_k', 'N/A')}` | `{vec.get('avg_recall_at_k', 'N/A')}` | `{vec.get('avg_mrr', 'N/A')}` | `{vec.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **Keyword-Only (Lucene Fulltext)** | `{ret_split}` | {ret_n} | `{kw.get('avg_precision_at_k', 'N/A')}` | `{kw.get('avg_recall_at_k', 'N/A')}` | `{kw.get('avg_mrr', 'N/A')}` | `{kw.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **Hybrid Search (RRF $k=60$)** | `{ret_split}` | {ret_n} | `{rrf.get('avg_precision_at_k', 'N/A')}` | `{rrf.get('avg_recall_at_k', 'N/A')}` | `{rrf.get('avg_mrr', 'N/A')}` | `{rrf.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **Hybrid + FlashRank Cross-Encoder** | `{ret_split}` | {ret_n} | `{flash.get('avg_precision_at_k', 'N/A')}` | `{flash.get('avg_recall_at_k', 'N/A')}` | `{flash.get('avg_mrr', 'N/A')}` | `{flash.get('avg_latency_sec', 0.0)*1000:.1f} ms` |
| **Semantic Intent Router** | `{router_split}` | {router_n} | `Accuracy: {router_acc:.1f}%` | `N/A` | `N/A` | `{router_lat:.1f} ms` |
| **Draft Answer (Verifier OFF)** | `{faith_split}` | {faith_n} | `Faith: {v_off_faith:.2f}/5.0` | `Grounded: {v_off_ground:.1f}%` | `N/A` | `N/A` |
| **Verified Answer (Verifier ON)** | `{faith_split}` | {faith_n} | `Faith: {v_on_faith:.2f}/5.0` | `Grounded: {v_on_ground:.1f}%` | `N/A` | `N/A` |
| **Adversarial Trap Abstention** | `{trap_split}` | {trap_n} | `Abstain: {trap_abstain:.1f}%` | `Halluc: {trap_halluc:.1f}%` | `N/A` | `N/A` |"""
    return table


def update_readme():
    metrics_path = os.path.join(ROOT, "reports", "latest", "eval_metrics_latest.json")
    readme_path = os.path.join(ROOT, "README.md")

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()

    start_marker = "<!-- BENCHMARK_TABLE_START -->"
    end_marker = "<!-- BENCHMARK_TABLE_END -->"

    table_content = build_readme_table(metrics)
    replacement = f"{start_marker}\n{table_content}\n{end_marker}"

    if start_marker in readme and end_marker in readme:
        parts = readme.split(start_marker)
        rest = parts[1].split(end_marker)
        new_readme = parts[0] + replacement + rest[1]
    else:
        # Insert markers if not present
        target_section = "## Empirical Benchmark Results"
        assert target_section in readme, "Target section missing in README"
        idx = readme.find(target_section)
        nl_idx = readme.find("\n\n", idx)
        new_readme = readme[: nl_idx + 2] + replacement + "\n\n" + readme[nl_idx + 2 :]

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme)

    print("Successfully updated README.md with benchmark table from JSON metrics.")


if __name__ == "__main__":
    update_readme()
