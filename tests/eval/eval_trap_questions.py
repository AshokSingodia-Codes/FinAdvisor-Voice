"""
Step 3 — Trap / Out-of-Corpus Hallucination Benchmark
Evaluates whether the system properly abstains, refuses, or qualifies answers on:
- Unindexed companies (e.g. Acme Space Mining 2024 revenue)
- Non-existent executive names & fake metrics
- Private or impossible financial facts

Calculates Abstention Accuracy Rate and Hallucination Incident Rate.
"""
import os
import sys
import json
import time
from typing import Dict, Any, List

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from graph.workflow import app_graph
from tests.eval.judge_prompts import evaluate_trap_abstention

def load_gold_set(filepath: str = None) -> List[Dict[str, Any]]:
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "gold_set.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def run_trap_evaluation(gold_set_path: str = None) -> Dict[str, Any]:
    questions = load_gold_set(gold_set_path)
    trap_questions = [q for q in questions if q.get("is_out_of_corpus", False) or q.get("category") == "trap_out_of_corpus"]
    
    print("\n=======================================================")
    print("🛡️ FinAdvisor-X Trap & Out-of-Corpus Hallucination Benchmark")
    print("=======================================================")
    print(f"Testing {len(trap_questions)} adversarial/trap queries for safe abstention...\n")
    
    results = []
    correct_abstentions = 0
    hallucinations = 0
    judge_errors = 0
    errors = 0
    
    for i, item in enumerate(trap_questions, 1):
        q = item["question"]
        expected_behavior = item.get("ground_truth_answer", "Explicitly state information is unavailable without fabricating numbers")
        
        t0 = time.time()
        generated_answer = ""
        has_error = False
        error_msg = ""
        
        for attempt in range(3):
            try:
                state_input = {
                    "original_question": q,
                    "current_question": q,
                    "user_id": "eval_test_user",
                    "memory_context": "None"
                }
                output = app_graph.invoke(state_input)
                generated_answer = output.get("final_answer") or output.get("draft_answer") or ""
                has_error = False
                break
            except Exception as e:
                has_error = True
                error_msg = str(e)
                print(f"      Attempt {attempt+1} error: {e}")
                if attempt < 2:
                    time.sleep(5 * (2 ** attempt))
                    
        latency = time.time() - t0
        
        if has_error:
            errors += 1
            generated_answer = f"Error during graph execution: {error_msg}"
            status = "❌ ERROR"
            print(f"[{i:02d}/{len(trap_questions):02d}] {status} | Q: {q[:50]}...")
            
            results.append({
                "id": item.get("id"),
                "question": q,
                "expected_behavior": expected_behavior,
                "generated_answer": generated_answer,
                "status": "error",
                "error_detail": error_msg,
                "latency_sec": round(latency, 4)
            })
            continue
            
        # Evaluate with LLM Judge
        eval_result = evaluate_trap_abstention(
            question=q,
            answer=generated_answer,
            expected_behavior=expected_behavior
        )
        
        if getattr(eval_result, "judge_error", False):
            judge_errors += 1
            item_status = "judge_error"
            status_str = "⚠️ JUDGE_ERROR"
        elif eval_result.correctly_abstained:
            correct_abstentions += 1
            item_status = "abstained"
            status_str = "🛡️ ABSTAINED"
        elif eval_result.hallucinated_facts:
            hallucinations += 1
            item_status = "hallucinated"
            status_str = "⚠️ HALLUCINATED"
        else:
            item_status = "unknown"
            status_str = "❓ UNKNOWN"
            
        print(f"[{i:02d}/{len(trap_questions):02d}] {status_str} | Q: {q[:50]}...")
        print(f"      Judge Reasoning: {eval_result.reasoning}")
        
        results.append({
            "id": item.get("id"),
            "question": q,
            "expected_behavior": expected_behavior,
            "generated_answer": generated_answer,
            "status": item_status,
            "correctly_abstained": eval_result.correctly_abstained,
            "hallucinated_facts": eval_result.hallucinated_facts,
            "judge_error": getattr(eval_result, "judge_error", False),
            "reasoning": eval_result.reasoning,
            "latency_sec": round(latency, 4)
        })

    total = len(trap_questions)
    real_verdicts = correct_abstentions + hallucinations
    
    if real_verdicts > 0:
        abstention_rate = (correct_abstentions / real_verdicts) * 100
        hallucination_rate = (hallucinations / real_verdicts) * 100
    else:
        abstention_rate = 0.0
        hallucination_rate = 0.0
        
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_trap_questions": total,
        "counts": {
            "abstained": correct_abstentions,
            "hallucinated": hallucinations,
            "judge_error": judge_errors,
            "generation_error": errors,
            "real_verdicts": real_verdicts
        },
        "abstention_rate_pct": round(abstention_rate, 2),
        "hallucination_rate_pct": round(hallucination_rate, 2),
        "evaluations": results
    }
    
    # Save results to reports/
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_file = os.path.join(reports_dir, "trap_eval.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
        
    print("\n=======================================================")
    print(f"🛡️ TRAP QUESTION BENCHMARK SUMMARY")
    print("=======================================================")
    print(f"Total Trap Questions Tested:     {total}")
    print(f"  - Correctly Abstained:         {correct_abstentions}")
    print(f"  - Hallucinated:                {hallucinations}")
    print(f"  - Judge Errors:                {judge_errors}")
    print(f"  - Generation Errors:           {errors}")
    print(f"  - Real Verdicts Evaluated:     {real_verdicts}")
    print(f"Safe Abstention Rate (Real):     {abstention_rate:.1f}%")
    print(f"Hallucination Rate (Real):       {hallucination_rate:.1f}%")
    print(f"💾 Report saved to: {report_file}")
    print("=======================================================\n")
    
    return report_data

if __name__ == "__main__":
    run_trap_evaluation()
