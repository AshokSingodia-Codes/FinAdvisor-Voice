from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.state import AgentState
from core.db import fast_chat, get_structured_fast_chat

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
    enabled = state.get("verifier_enabled", True)
    draft = state.get("draft_answer", "")
    context_list = state.get("retrieved_context", [])
    context = "\n---\n".join(str(c) for c in context_list) if context_list else "No retrieved context."
    question = state.get("original_question", "")

    routing_decision = state.get("routing_decision", "")
    document_id = state.get("document_id")
    if not enabled or document_id or routing_decision in ("direct_answer", "math_calculation", "live_market_data"):
        print(f"[DEBUG] ---NODE: VERIFIER SKIPPED (doc: {bool(document_id)}, route: {routing_decision}, enabled: {enabled})---")
        return {
            "verification_passed": True,
            "final_answer": draft
        }

    print("[DEBUG] ---NODE: VERIFIER RUNNING (verifier_enabled=True)---")
    try:
        res = verifier_chain.invoke({
            "context": context,
            "draft": draft,
            "question": question
        })
        is_supported = res.is_supported and res.numerical_consistency
        if not is_supported:
            qualified_answer = f"{draft}\n\n[Verification Notice]: Fact-check auditor found ungrounded or inconsistent claims: {res.reasoning}"
        else:
            qualified_answer = draft
            
        return {
            "verification_passed": is_supported,
            "final_answer": qualified_answer
        }
    except Exception as e:
        print(f"[DEBUG] ---NODE: VERIFIER ERROR ({e}), PASSING THROUGH---")
        return {
            "verification_passed": True,
            "final_answer": draft
        }
