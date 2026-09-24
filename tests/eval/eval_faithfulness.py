"""
Step 4 — Answer Faithfulness & Self-RAG Verifier Ablation Benchmark
Evaluates answer grounding and factual alignment against retrieved context chunks using LLM-as-a-Judge.
Runs ablation comparing:
  1. Verifier OFF (Raw Draft Answer)
  2. Verifier ON (Self-RAG Consistency Check & Corrective Refinement)

Calculates Mean Faithfulness Score (1-5), Grounding Rate (%), and Verifier Lift.
"""
import os
import sys
import json
import time
from typing import Dict, Any, List

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from graph.workflow import app_graph
from nodes.verifier import verifier_chain
from tests.eval.judge_prompts import evaluate_faithfulness

def load_gold_set(filepath: str = None) -> List[Dict[str, Any]]:
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "gold_set.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def run_faithfulness_evaluation(gold_set_path: str = None, sample_size: int = 5) -> Dict[str, Any]:
    questions = load_gold_set(gold_set_path)
    
    # Select 5 representative gold questions spanning 10k_factual, finance_textbook, and investment_literature
    target_ids = ["q001", "q002", "q016", "q025", "q029"]
    eval_subset = [q for q in questions if q.get("id") in target_ids]
    if len(eval_subset) < 5:
        fallback_subset = [q for q in questions if not q.get("is_out_of_corpus", False) and q.get("category") in ["10k_factual", "factual_10k", "corporate_finance_textbook", "finance_textbook", "investment_literature"]]
        eval_subset = fallback_subset[:sample_size]
        
    print("\n=======================================================")
    print("⚖️ FinAdvisor-X Answer Faithfulness & Self-RAG Ablation Benchmark")
    print("=======================================================")
    print(f"Evaluating {len(eval_subset)} in-corpus queries for factual context grounding...\n")
    
    draft_scores = []
    draft_grounded_flags = []
    
    verified_scores = []
    verified_grounded_flags = []
    
    item_results = []
    
    for i, item in enumerate(eval_subset, 1):
        q = item["question"]
        t0 = time.time()
        
        # 1. Run Graph with Verifier OFF
        draft_answer = ""
        retrieved_chunks = []
        context_str = "No retrieved context."
        for attempt in range(3):
            try:
                state_off = {
                    "original_question": q,
                    "current_question": q,
                    "user_id": "eval_test_user",
                    "memory_context": "None",
                    "verifier_enabled": False
                }
                print(f"[{i:02d}/{len(eval_subset):02d}] Invoking Graph [Verifier OFF] (attempt {attempt+1})...", flush=True)
                output_off = app_graph.invoke(state_off)
                draft_answer = output_off.get("draft_answer") or output_off.get("final_answer") or ""
                retrieved_chunks = output_off.get("retrieved_context") or []
                context_str = "\n---\n".join([str(c) for c in retrieved_chunks]) if retrieved_chunks else "No retrieved context."
                break
            except Exception as e:
                print(f"      [Verifier OFF] Attempt {attempt+1} error: {e}")
                if attempt < 2:
                    time.sleep(5 * (2 ** attempt))
                else:
                    draft_answer = f"Error during graph execution: {e}"
                    context_str = "Error"

        # Judge Draft Answer (Verifier OFF)
        eval_draft = evaluate_faithfulness(question=q, context=context_str, answer=draft_answer)
        draft_scores.append(eval_draft.score)
        draft_grounded_flags.append(eval_draft.is_grounded)
        
        # Rate-limiting delay between graph invocations
        time.sleep(12)

        # 2. Run Graph with Verifier ON
        verified_answer = ""
        for attempt in range(3):
            try:
                state_on = {
                    "original_question": q,
                    "current_question": q,
                    "user_id": "eval_test_user",
                    "memory_context": "None",
                    "verifier_enabled": True
                }
                print(f"[{i:02d}/{len(eval_subset):02d}] Invoking Graph [Verifier ON] (attempt {attempt+1})...")
                output_on = app_graph.invoke(state_on)
                verified_answer = output_on.get("final_answer") or output_on.get("draft_answer") or ""
                break
            except Exception as e:
                print(f"      [Verifier ON] Attempt {attempt+1} error: {e}")
                if attempt < 2:
                    time.sleep(5 * (2 ** attempt))
                else:
                    verified_answer = draft_answer
            
        # Judge Verified Answer (Verifier ON)
        eval_verified = evaluate_faithfulness(question=q, context=context_str, answer=verified_answer)
        verified_scores.append(eval_verified.score)
        verified_grounded_flags.append(eval_verified.is_grounded)
        
        latency = time.time() - t0
        
        print(f"[{i:02d}/{len(eval_subset):02d}] Draft Score: {eval_draft.score}/5 | Verified Score: {eval_verified.score}/5 | {q[:45]}...")
        if eval_draft.unsupported_claims:
            print(f"      Ungrounded Claims: {eval_draft.unsupported_claims}")
            
        item_results.append({
            "id": item.get("id"),
            "question": q,
            "category": item.get("category"),
            "draft_answer": draft_answer,
            "draft_faithfulness_score": eval_draft.score,
            "draft_is_grounded": eval_draft.is_grounded,
            "draft_unsupported_claims": eval_draft.unsupported_claims,
            "verified_faithfulness_score": eval_verified.score,
            "verified_is_grounded": eval_verified.is_grounded,
            "latency_sec": round(latency, 4)
        })

    n = max(len(draft_scores), 1)
    avg_draft_score = sum(draft_scores) / n
    draft_grounding_pct = (sum(1 for g in draft_grounded_flags if g) / n) * 100
    
    avg_verified_score = sum(verified_scores) / n
    verified_grounding_pct = (sum(1 for g in verified_grounded_flags if g) / n) * 100
    
    score_lift_pct = ((avg_verified_score - avg_draft_score) / max(avg_draft_score, 0.01)) * 100
    grounding_lift_pct = verified_grounding_pct - draft_grounding_pct
    
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_queries_evaluated": len(eval_subset),
        "verifier_off": {
            "mean_faithfulness_score": round(avg_draft_score, 3),
            "grounding_rate_pct": round(draft_grounding_pct, 2)
        },
        "verifier_on": {
            "mean_faithfulness_score": round(avg_verified_score, 3),
            "grounding_rate_pct": round(verified_grounding_pct, 2)
        },
        "verifier_lift": {
            "faithfulness_score_lift_pct": round(score_lift_pct, 2),
            "grounding_rate_lift_pct_pts": round(grounding_lift_pct, 2)
        },
        "evaluations": item_results
    }
    
    # Save results to reports/
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_file = os.path.join(reports_dir, "faithfulness_eval.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
        
    print("\n=======================================================")
    print(f"⚖️ FAITHFULNESS & SELF-RAG VERIFIER SUMMARY")
    print("=======================================================")
    print(f"Configuration          | Mean Faithfulness (1-5) | Grounding Rate (%) |")
    print(f"-----------------------|-------------------------|--------------------|")
    print(f"Verifier OFF (Draft)   | {avg_draft_score:<23.2f} | {draft_grounding_pct:<18.1f}% |")
    print(f"Verifier ON (Self-RAG) | {avg_verified_score:<23.2f} | {verified_grounding_pct:<18.1f}% |")
    print("-------------------------------------------------------")
    print(f"🚀 Self-RAG Grounding Improvement: +{grounding_lift_pct:.1f}% pts")
    print(f"💾 Report saved to: {report_file}")
    print("=======================================================\n")
    
    return report_data

if __name__ == "__main__":
    run_faithfulness_evaluation()
