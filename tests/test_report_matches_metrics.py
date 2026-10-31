"""
Test to ensure README and reports/latest/eval_report_latest.md match
the exact values and computed unrounded deltas from reports/latest/eval_metrics_latest.json.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_reports_latest_matches_json_metrics():
    metrics_path = os.path.join(ROOT, "reports", "latest", "eval_metrics_latest.json")
    report_path = os.path.join(ROOT, "reports", "latest", "eval_report_latest.md")
    readme_path = os.path.join(ROOT, "README.md")

    assert os.path.exists(metrics_path), "eval_metrics_latest.json missing"
    assert os.path.exists(report_path), "eval_report_latest.md missing"
    assert os.path.exists(readme_path), "README.md missing"

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    with open(report_path, "r", encoding="utf-8") as f:
        report_text = f.read()

    with open(readme_path, "r", encoding="utf-8") as f:
        readme_text = f.read()

    # 1. Retrieval values
    r_cfg = metrics["retrieval"]["configurations"]
    vec_p = r_cfg["vector_only"]["avg_precision_at_k"]
    vec_r = r_cfg["vector_only"]["avg_recall_at_k"]
    vec_mrr = r_cfg["vector_only"]["avg_mrr"]

    rrf_p = r_cfg["hybrid_rrf"]["avg_precision_at_k"]
    rrf_r = r_cfg["hybrid_rrf"]["avg_recall_at_k"]
    rrf_mrr = r_cfg["hybrid_rrf"]["avg_mrr"]

    flash_p = r_cfg["hybrid_rrf_flashrank"]["avg_precision_at_k"]
    flash_mrr = r_cfg["hybrid_rrf_flashrank"]["avg_mrr"]
    flash_lat = r_cfg["hybrid_rrf_flashrank"]["avg_latency_sec"]
    rrf_lat = r_cfg["hybrid_rrf"]["avg_latency_sec"]

    # Verify unrounded deltas
    rel_h_rec = (rrf_r - vec_r) / vec_r * 100.0
    rel_h_mrr = (rrf_mrr - vec_mrr) / vec_mrr * 100.0
    rel_f_p = (flash_p - rrf_p) / rrf_p * 100.0
    rel_f_mrr = (flash_mrr - rrf_mrr) / rrf_mrr * 100.0

    assert f"{rel_h_rec:+.2f}%" in report_text or f"{rel_h_rec:.2f}%" in report_text
    assert f"{rel_h_mrr:+.2f}%" in report_text or f"{rel_h_mrr:.2f}%" in report_text
    assert f"{rel_f_p:+.2f}%" in report_text or f"{rel_f_p:.2f}%" in report_text
    assert f"{rel_f_mrr:+.2f}%" in report_text or f"{rel_f_mrr:.2f}%" in report_text

    # 2. Router accuracy
    router_acc = metrics["router"]["overall_accuracy"]
    acc_str = f"{router_acc*100:.1f}%"
    assert acc_str in report_text
    assert acc_str in readme_text

    # 3. Verifier values
    v_off = metrics["faithfulness"]["verifier_off"]["mean_faithfulness_score"]
    v_on = metrics["faithfulness"]["verifier_on"]["mean_faithfulness_score"]
    assert f"{v_off:.2f}" in report_text or f"{v_off:.1f}" in report_text
    assert f"{v_on:.2f}" in report_text or f"{v_on:.1f}" in report_text
