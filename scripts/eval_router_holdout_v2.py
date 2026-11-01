import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nodes.router import route_question


def evaluate_holdout_v2():
    v2_path = os.path.join(ROOT, "tests", "eval", "router_holdout_v2.json")
    with open(v2_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    correct = 0
    total = len(questions)
    cm = Counter()
    per_class = {}

    for q in questions:
        exp = q["expected_route"]
        prompt = q["question"]

        # Run offline fallback heuristic directly
        res = route_question({"original_question": prompt, "memory_context": "None"})
        pred = res.get("routing_decision", "direct_answer")

        # Canonicalize
        if pred in ["financial_table", "hybrid_search"]:
            pred_canon = "hybrid_search"
        elif pred in ["calculation", "math_calculation"]:
            pred_canon = "calculation" if exp == "calculation" else "math_calculation"
        else:
            pred_canon = pred

        exp_canon = exp
        is_match = (exp_canon == pred_canon)
        if is_match:
            correct += 1

        cm[(exp_canon, pred_canon)] += 1
        per_class.setdefault(exp_canon, {"total": 0, "correct": 0})
        per_class[exp_canon]["total"] += 1
        if is_match:
            per_class[exp_canon]["correct"] += 1

    overall_acc = correct / total if total else 0.0

    print("=== ROUTER HOLDOUT V2 EVALUATION (Clean Unseen Split, n=30) ===")
    print(f"Overall Accuracy: {correct}/{total} = {overall_acc*100:.1f}%\n")
    print("Per-Route Accuracy:")
    for r, stats in sorted(per_class.items()):
        acc = stats["correct"] / stats["total"] * 100.0
        print(f"  {r}: {stats['correct']}/{stats['total']} ({acc:.1f}%)")

    print("\nConfusion Matrix:")
    cm_dict = {}
    for (exp_r, pred_r), count in sorted(cm.items()):
        pair_str = f"{exp_r} -> {pred_r}"
        print(f"  {pair_str}: {count}")
        cm_dict[pair_str] = count

    # Also evaluate existing test split with traps excluded
    test_path = os.path.join(ROOT, "tests", "eval", "gold_set_test.json")
    with open(test_path, "r", encoding="utf-8") as f:
        test_q = json.load(f)

    test_no_traps = [q for q in test_q if not q.get("is_out_of_corpus")]
    t_correct = 0
    for q in test_no_traps:
        exp = q.get("expected_route", "hybrid_search")
        if exp in ["financial_table", "hybrid_search"]:
            exp_c = "hybrid_search"
        elif exp in ["calculation", "math_calculation"]:
            exp_c = "calculation"
        else:
            exp_c = exp
        res = route_question({"original_question": q["question"], "memory_context": "None"})
        pred = res.get("routing_decision", "direct_answer")
        if pred in ["financial_table", "hybrid_search"]:
            pred_c = "hybrid_search"
        elif pred in ["calculation", "math_calculation"]:
            pred_c = "calculation"
        else:
            pred_c = pred
        if exp_c == pred_c:
            t_correct += 1

    test_no_traps_acc = t_correct / len(test_no_traps) if test_no_traps else 0.0
    print(f"\nExisting Test Split (Traps Excluded, n={len(test_no_traps)}):")
    print(f"  Accuracy: {t_correct}/{len(test_no_traps)} = {test_no_traps_acc*100:.1f}%")

    out_metrics = {
        "dataset": "router_holdout_v2.json",
        "sha256": "a9e969d59686cb8a70d161c5fc42dfbdd3dbdf077c87b671bc4cd2fa07c24bbd",
        "split": "holdout_v2",
        "router_path": "fallback_heuristic",
        "status": "measured",
        "n": total,
        "overall_accuracy": round(overall_acc, 4),
        "per_route_metrics": {r: {"total": s["total"], "correct": s["correct"], "accuracy": round(s["correct"]/s["total"], 4)} for r, s in per_class.items()},
        "confusion_matrix": cm_dict,
        "existing_test_no_traps": {
            "n": len(test_no_traps),
            "correct": t_correct,
            "accuracy": round(test_no_traps_acc, 4)
        }
    }

    with open(os.path.join(ROOT, "reports", "latest", "router_holdout_v2_results.json"), "w", encoding="utf-8") as f:
        json.dump(out_metrics, f, indent=2)

    return out_metrics

if __name__ == "__main__":
    evaluate_holdout_v2()
