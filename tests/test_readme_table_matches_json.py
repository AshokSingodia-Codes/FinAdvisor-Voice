"""
Test to ensure README results table matches reports/latest/eval_metrics_latest.json
and is properly formatted between marker comments.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_readme_table_matches_json():
    metrics_path = os.path.join(ROOT, "reports", "latest", "eval_metrics_latest.json")
    readme_path = os.path.join(ROOT, "README.md")

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()

    assert "<!-- BENCHMARK_TABLE_START -->" in readme
    assert "<!-- BENCHMARK_TABLE_END -->" in readme

    table_chunk = readme.split("<!-- BENCHMARK_TABLE_START -->")[1].split("<!-- BENCHMARK_TABLE_END -->")[0]

    # Verify Run column present in table header
    assert "| Pipeline Stage / Subsystem | Run | n |" in table_chunk

    # Verify retrieval precision and recall values from JSON
    r_cfg = metrics["retrieval"]["configurations"]
    vec_p = str(r_cfg["vector_only"]["avg_precision_at_k"])
    flash_p = str(r_cfg["hybrid_rrf_flashrank"]["avg_precision_at_k"])

    assert vec_p in table_chunk
    assert flash_p in table_chunk

    # Verify router accuracy from JSON
    router_acc = metrics["router"]["overall_accuracy"]
    acc_pct = f"{router_acc * 100:.1f}%"
    assert acc_pct in table_chunk

    # Verify verifier scores from JSON
    v_off = metrics["faithfulness"]["verifier_off"]["mean_faithfulness_score"]
    v_on = metrics["faithfulness"]["verifier_on"]["mean_faithfulness_score"]
    assert f"{v_off:.2f}" in table_chunk or f"{v_off:.1f}" in table_chunk
    assert f"{v_on:.2f}" in table_chunk or f"{v_on:.1f}" in table_chunk
