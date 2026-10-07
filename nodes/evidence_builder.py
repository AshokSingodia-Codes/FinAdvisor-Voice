import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from graph.state import AgentState
from core.db import synthesis_chat, fast_chat, chat
from nodes.router import classify_depth
from core.greeting_handler import is_greeting_or_chitchat, get_greeting_response

# ---------------------------------------------------------------------------
# FinAdvisor Response Writer Prompt
# Controls length, token consumption, and formatting based on depth
# ---------------------------------------------------------------------------
response_writer_prompt = ChatPromptTemplate.from_template("""You are FinAdvisor's executive response writer. You answer the user's financial question using ONLY the verified evidence provided below (retrieved documents, math results, live market data). Never invent numbers or facts not present in the evidence.

Formatting & Structure Guidelines:

1. EXECUTIVE DIRECT ANSWER (Top 1-2 lines):
   - Always start immediately with a direct, unambiguous 1-2 line answer or numerical bottom-line in bold.
   - Example: "**The total tax liability under the New Regime for ₹15 Lakh income is ₹1,04,000 (after standard deduction of ₹75,000).**"

2. EXECUTIVE SUMMARY / KEY HIGHLIGHTS:
   - Provide 3-5 concise bullet points highlighting key figures, rate/tax breakdown, rationale, or actionable insights.
   - Bold key numbers, percentages, or terms for fast scanning.

3. DETAILED BREAKDOWN & FORMULAS (When depth = "deep" or complex analysis):
   - Use clean markdown tables for tabular data, tax slabs, or balance sheet comparisons.
   - Include step-by-step arithmetic formulas where calculations were performed.
   - Integrate all facts seamlessly into the analysis without raw source or citation tags.

Formatting by depth:
If depth = "quick":
  - 1-2 lines direct answer + 1 optional line of key takeaway or next step. Maximum ~100 words.
  - No bloated boilerplate or redundant filler.

If depth = "summary":
  - 1-2 lines direct answer at the top.
  - Followed by 3-5 structured bullet points covering the core financial breakdown.

If depth = "deep":
  - 1-2 lines direct answer / executive verdict at the top.
  - Followed by full structured breakdown: key highlights, tables, tax/valuation mechanics, and formulas.

Universal rules, all depths:
  - Never fabricate facts or numbers not in evidence.
  - Match user's language (English/Hindi/Hinglish) and currency convention (₹ for Indian context, $ for USD/global).
  - Include 1-3 suggested follow-up actions enclosed in brackets at the very bottom, e.g. [Calculate tax under Old Regime] or [Check Reliance P/E ratio].
  - NEVER include raw citations or source tags like [Source: ...], 【Source: ...】, (Source: ...), or database tags in the response text. Present all facts directly and authoritatively.
  - Never restate the user's question back to them before answering.

---
depth: {depth}
user_question: {query}
verified_evidence: {evidence_summary}
math_results: {tool_results}
chat_history: {chat_history}
---

Write only the answer. No meta-commentary about your formatting choices.""")

quick_builder_chain = response_writer_prompt | fast_chat | StrOutputParser()
builder_chain = response_writer_prompt | synthesis_chat | StrOutputParser()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_user_facing_text(text: str) -> str:
    if not text:
        return text
    # Remove verification/audit notices
    text = re.sub(r'\[Verification Notice\]:[^\n]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[Audit Notice\]:[^\n]*', '', text, flags=re.IGNORECASE)
    # Remove unicode and bracketed Source citations
    text = re.sub(r'【\s*Source:[^】]*】', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\s*Source:[^\]]*\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(\s*Source:[^)]*\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\s*\*{0,2}Source:\*{0,2}\s*[^\n]*$', '', text, flags=re.IGNORECASE | re.MULTILINE)
    # Clean up double newlines or stray whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def format_history_for_builder(history, max_turns=6):
    if not history:
        return "No previous conversation."
    formatted = []
    for msg in history[-max_turns:]:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "").strip()
        formatted.append(f"[{role}]: {content}")
    return "\n\n".join(formatted)


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------

def build_evidence(state: AgentState):
    print("---NODE: EVIDENCE BUILDER---")
    question = state.get("resolved_query") or state.get("current_question") or state.get("original_question", "")
    memory_context = state.get("memory_context", "")

    # Token Optimization: Deduplicate retrieved chunks and bound strictly to Top 3 chunks (<700 tokens total)
    raw_retrieved = state.get("retrieved_context", [])
    seen_hashes = set()
    compact_retrieved = []
    total_chars = 0
    MAX_TOTAL_CHARS = 2800  # ~650 - 750 tokens ceiling (prevents Groq 8k TPM exhaustion)
    
    for item in raw_retrieved:
        txt = str(item).strip()
        if not txt:
            continue
        
        # Normalized signature for deduplication
        norm_sig = " ".join(txt.split()[:40]).lower()
        if norm_sig in seen_hashes:
            continue
        seen_hashes.add(norm_sig)
        
        # Check cumulative token boundary
        if total_chars + len(txt) > MAX_TOTAL_CHARS:
            remaining_allowance = MAX_TOTAL_CHARS - total_chars
            if remaining_allowance > 300:
                # Safe newline truncate to avoid breaking markdown tables or numbers
                cut_idx = txt.rfind("\n", 0, remaining_allowance)
                if cut_idx > 150:
                    txt = txt[:cut_idx] + "\n[... Segment bounded for token efficiency ...]"
                    compact_retrieved.append(txt)
            break

        compact_retrieved.append(txt)
        total_chars += len(txt)
        if len(compact_retrieved) >= 3:
            break

    context = "\n\n---\n\n".join(compact_retrieved) if compact_retrieved else "No additional reference documents retrieved."
    document_id = state.get("document_id")

    if not document_id:
        if state.get("final_answer") and state.get("routing_decision") in ("direct_answer", "live_market_data"):
            ans = state["final_answer"]
            return {"draft_answer": ans, "final_answer": ans}
        is_greeting, category = is_greeting_or_chitchat(question)
        if is_greeting and category:
            print(f"  [Evidence Builder: INSTANT GREETING FAST-PATH] category='{category}'")
            reply = get_greeting_response(category, question)
            return {"draft_answer": reply, "final_answer": reply}

    depth = state.get("depth") or classify_depth(question)
    tool_results = state.get("draft_answer") or "None"
    chat_history = memory_context if memory_context else "None"

    try:
        print(f"  [Evidence Builder: SYNTHESIS] depth='{depth}', doc={bool(document_id)} ({len(compact_retrieved)} chunks bounded)")
        target_chain = quick_builder_chain if depth == "quick" else builder_chain
        answer = target_chain.invoke({
            "depth": depth,
            "query": question,
            "evidence_summary": context,
            "tool_results": tool_results,
            "chat_history": chat_history,
        })
        answer = clean_user_facing_text(answer)
    except Exception as e:
        print(f"[evidence_builder error]: {e}")
        answer = (
            "I encountered a temporary service issue while processing this request and cannot reliably synthesize "
            "an answer. I do not have verified data available to answer this question. Please try again later."
        )

    return {
        "draft_answer": answer,
        "final_answer": answer,
    }


