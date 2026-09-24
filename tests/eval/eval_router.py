"""
Step 2 — Semantic Router Accuracy & Classification Benchmark
Evaluates the LangGraph Router against all 50 labeled queries across:
- hybrid_search
- decompose
- calculation / math_calculation
- live_market_data
- direct_answer

Computes Overall Accuracy, Confusion Matrix, and Per-Class Precision / Recall / F1.
"""
import os
import sys
import json
import time
from typing import Dict, Any, List
from collections import defaultdict

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nodes.router import route_question, router_chain

def load_gold_set(filepath: str = None) -> List[Dict[str, Any]]:
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "gold_set.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def run_router_evaluation(gold_set_path: str = None) -> Dict[str, Any]:
    questions = load_gold_set(gold_set_path)
    
    print("\n=======================================================")
    print("🚦 FinAdvisor-X Semantic Router Benchmark")
    print("=======================================================")
    print(f"Evaluating router classification across {len(questions)} labeled gold queries...\n")
    
    y_true = []
    y_pred = []
    latencies = []
    per_item_results = []
    
    for i, item in enumerate(questions, 1):
        q = item["question"]
        expected = item.get("expected_route", "hybrid_search")
        
        # Normalize route mapping if aliases exist
        if expected in ["financial_table", "hybrid_search"]:
            expected_canonical = "hybrid_search"
        elif expected in ["calculation", "math_calculation"]:
            expected_canonical = "calculation"
        else:
            expected_canonical = expected
            
        t0 = time.time()
        try:
            res = route_question({"original_question": q, "memory_context": "None"})
            actual = res.get("routing_decision", "direct_answer")
        except Exception as e:
            actual = "direct_answer"
        latency = time.time() - t0
        latencies.append(latency)
        
        # Apply ROUTE_EQUIVALENCE (Option B: end-to-end retrieval equivalence)
        ROUTE_EQUIVALENCE = {"financial_table": "hybrid_search"}
        actual_mapped = ROUTE_EQUIVALENCE.get(actual, actual)
        
        # Normalize actual route
        if actual_mapped in ["financial_table", "hybrid_search"]:
            actual_canonical = "hybrid_search"
        elif actual_mapped in ["calculation", "math_calculation"]:
            actual_canonical = "calculation"
        else:
            actual_canonical = actual_mapped
            
        is_match = (expected_canonical == actual_canonical)
        y_true.append(expected_canonical)
        y_pred.append(actual_canonical)
        
        per_item_results.append({
            "id": item.get("id"),
            "question": q,
            "category": item.get("category"),
            "expected_route": expected_canonical,
            "predicted_route": actual_canonical,
            "is_correct": is_match,
            "latency_sec": round(latency, 4)
        })
        
        status_sym = "✅" if is_match else "❌"
        print(f"[{i:02d}/{len(questions):02d}] {status_sym} Expected: {expected_canonical:<16} | Predicted: {actual_canonical:<16} | {q[:40]}...")

    # Calculate Accuracy and per-class metrics
    classes = sorted(list(set(y_true + y_pred)))
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)
    total_correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    accuracy = total_correct / max(len(y_true), 1)
    
    for yt, yp in zip(y_true, y_pred):
        if yt == yp:
            tp[yt] += 1
        else:
            fp[yp] += 1
            fn[yt] += 1
            
    per_class_metrics = {}
    for c in classes:
        p = tp[c] / max(tp[c] + fp[c], 1) if (tp[c] + fp[c]) > 0 else 0.0
        r = tp[c] / max(tp[c] + fn[c], 1) if (tp[c] + fn[c]) > 0 else 0.0
        f1 = (2 * p * r) / max(p + r, 1e-6) if (p + r) > 0 else 0.0
        per_class_metrics[c] = {
            "support": tp[c] + fn[c],
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1_score": round(f1, 4)
        }
        
    avg_latency = sum(latencies) / max(len(latencies), 1)
    
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_queries": len(questions),
        "overall_accuracy": round(accuracy, 4),
        "avg_router_latency_ms": round(avg_latency * 1000, 2),
        "per_class_metrics": per_class_metrics,
        "details": per_item_results
    }
    
    # Save results to reports/
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_file = os.path.join(reports_dir, "router_eval.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
        
    print("\n=======================================================")
    print(f"🎯 ROUTER BENCHMARK SUMMARY (Overall Accuracy: {accuracy*100:.1f}%)")
    print("=======================================================")
    print(f"| Route Intent       | Support | Precision | Recall | F1-Score |")
    print(f"|--------------------|---------|-----------|--------|----------|")
    for c, m in per_class_metrics.items():
        print(f"| {c:<18} | {m['support']:<7} | {m['precision']:<9.3f} | {m['recall']:<6.3f} | {m['f1_score']:<8.3f} |")
    print("-------------------------------------------------------")
    print(f"⚡ Average Router Latency: {avg_latency*1000:.1f} ms")
    print(f"💾 Report saved to: {report_file}")
    print("=======================================================\n")
    
    return report_data

if __name__ == "__main__":
    run_router_evaluation()
