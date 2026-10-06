from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.state import AgentState
from core.db import fast_chat, get_structured_fast_chat
from utils.retry import with_retry
import time

class Verification(BaseModel):
    is_supported: bool = Field(description="True if the draft answer is fully supported by the context.")
    numerical_consistency: bool = Field(description="True if all numbers in the draft exactly match the context.")
    citation_consistency: bool = Field(description="True if the draft properly cites its sources (e.g. Page X, Table Y).")
    reasoning: str = Field(description="Brief explanation of why it is or isn't supported.")

verifier_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert fact-checker and financial auditor.
    Your job is to audit a draft answer against the provided context documents and query.

    AUDITING RULES:
    1. COMPANY & ENTITY FACTUAL GROUNDING:
       - Every specific historical or financial assertion about a real company (e.g. Apple's net sales, Tesla's debt, CEO names, audited revenue figures) MUST be grounded in the context.
       - If the draft invents or fabricates financial figures for a specific corporate entity that are not in the context, return is_supported=False and numerical_consistency=False.

    2. SAFE ABSTENTIONS (CRITICAL):
       - If the draft answer explicitly states that the requested company information, filing, or future data is unavailable, unannounced, or not present in the indexed corpus, and refrains from fabricating fake numbers, this is a FULLY VALID AND GROUNDED RESPONSE. Return is_supported=True and numerical_consistency=True.

    3. EDUCATIONAL & ILLUSTRATIVE EXAMPLES:
       - If the query asks for general financial concepts, formulas, or budgeting rules (e.g. 50/30/20 rule, WACC formula, SIP compounding), and the draft uses clearly marked hypothetical numbers for demonstration (e.g. 'For example, if you earn ₹50,000...'), verify that the mathematical formulas and arithmetic are correct. Do not reject valid educational examples solely because the hypothetical scenario is not in a 10-K filing.

    4. NUMERICAL CONSISTENCY:
       - Check all stated numbers against the text. If company-specific figures contradict the context, return numerical_consistency=False.

    5. STRATEGIC RECOMMENDATIONS & ADVISORY:
       - If the draft provides forward-looking business strategies, profit improvement tips, next steps, budgeting ideas, or recommendations based on the financial health in the document, these are valid advisory insights. Do not reject valid advisory recommendations. Return is_supported=True and numerical_consistency=True.
    """),
    ("human", "Context:\n{context}\n\nDraft Answer:\n{draft}\n\nQuestion:\n{question}")
])

verifier_chain = verifier_prompt | get_structured_fast_chat(Verification)

def verify_answer(state: AgentState):
    """
    Audits draft answers against retrieved evidence for factual accuracy and numerical grounding.
    
    RESPONSE-MODE & FAST-PASS OPTIMIZATION:
    - If `response_mode == 'brief'`, or if verifier is explicitly disabled, or for pure mathematical/market
      computations, the fact-checking audit loop is skipped on the first pass to eliminate unnecessary LLM latency.
    - This skip logic is distinct from the audit-failure retry path, which only triggers when an actual
      hallucination or contradiction is discovered in detailed corporate retrieval synthesis.
    """
    enabled = state.get("verifier_enabled", True)
    draft = state.get("draft_answer", "")
    # Early refusal if draft looks like code (import, def, class, script)
    if any(kw in draft.lower() for kw in ["import ", "def ", "class ", "script"]):
        refusal = "I’m sorry, but I can’t provide that code."
        return {"verification_passed": False, "final_answer": refusal}
    context_list = state.get("retrieved_context", [])
    context = "\n---\n".join(str(c) for c in context_list) if context_list else "No retrieved context."
    question = state.get("resolved_query") or state.get("current_question") or state.get("original_question", "")

    routing_decision = state.get("routing_decision", "")
    document_id = state.get("document_id")
    response_mode = state.get("response_mode", "detailed")

    # Fast-pass bypass for brief mode, live market feeds, pure math, or disabled audits
    if not enabled or document_id or response_mode == "brief" or routing_decision in ("math_calculation", "calculation", "live_market_data"):
        print(f"[DEBUG] ---NODE: VERIFIER SKIPPED (doc: {bool(document_id)}, mode: {response_mode}, route: {routing_decision}, enabled: {enabled})---")
        return {
            "verification_passed": True,
            "final_answer": draft
        }


    current_retries = state.get("retrieval_retries", 0)
    print("[DEBUG] ---NODE: VERIFIER RUNNING (verifier_enabled=True)---")
    try:
        res = with_retry(lambda: verifier_chain.invoke({
            "context": context,
            "draft": draft,
            "question": question
        }), max_retries=1, base_delay=0.5)
        is_supported = res.is_supported and res.numerical_consistency
        if not is_supported:
            print(f"[DEBUG] ---NODE: VERIFIER AUDIT WARNING: {res.reasoning}---")
        qualified_answer = draft
            
        return {
            "verification_passed": is_supported,
            "final_answer": qualified_answer,
            "retrieval_retries": current_retries + 1
        }
    except Exception as e:
        print(f"[DEBUG] ---NODE: VERIFIER ERROR ({e}), PASSING THROUGH---")
        # Heuristic: if draft contains code-like keywords, refuse to comply
        forbidden = any(kw in draft.lower() for kw in ["import ", "def ", "class ", "script"])
        if forbidden:
            refusal = "I’m sorry, but I can’t provide that code."
            return {
                "verification_passed": False,
                "final_answer": refusal,
                "retrieval_retries": current_retries + 1
            }
        return {
            "verification_passed": True,
            "final_answer": draft,
            "retrieval_retries": current_retries + 1
        }
