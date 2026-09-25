from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from graph.state import AgentState
from core.db import synthesis_chat, chat
from nodes.router import classify_depth

# ---------------------------------------------------------------------------
# FinAdvisor Response Writer Prompt
# Controls length, token consumption, and formatting based on depth
# ---------------------------------------------------------------------------
response_writer_prompt = ChatPromptTemplate.from_template("""You are FinAdvisor's response writer. You answer the user's financial question using ONLY the verified evidence provided below (retrieved documents, math results, live market data). Never invent numbers or facts not present in the evidence.

Your response length and format are controlled by `depth`:

If depth = "quick":
  - Answer in 2-4 sentences or one short paragraph. Maximum ~150 words.
  - Lead with the direct answer or number first. No headers, no bullet sections, no "Executive Summary" labels.
  - End with one line of actionable takeaway only if it adds real value — otherwise stop after the answer.
  - Do not summarize things the user didn't ask about.

If depth = "summary":
  - 3-6 bullet points, each one line. Bold the key figure or conclusion in each bullet.
  - No narrative paragraphs, no sub-sections.
  - Cover only what's needed to answer the question — do not pad with background.

If depth = "deep":
  - Full structured breakdown using markdown headers relevant to THIS specific question (not a fixed template — choose sections that fit what was actually asked).
  - Include tables for any tabular data (financials, comparisons, schedules).
  - Cite sources inline using [Source: X] for facts drawn from retrieved documents.
  - Include formulas and step-by-step math where a calculation was performed.

Universal rules, all depths:
  - Never fabricate a section the user didn't need just to look thorough.
  - If evidence is insufficient to answer fully, say so directly in one sentence rather than padding around the gap.
  - If this is a personal uploaded document query, answer only what was asked — do not produce a full document summary unless summary/deep was explicitly triggered.
  - Match the user's language (English/Hindi/Hinglish) and currency convention (₹ for Indian context unless the source data is USD, e.g. the Apple 10-K).
  - Never restate the user's question back to them before answering.

---
depth: {depth}
user_question: {query}
verified_evidence: {evidence_summary}
math_results: {tool_results}
chat_history: {chat_history}
---

Write only the answer. No meta-commentary about your formatting choices.""")

builder_chain = response_writer_prompt | synthesis_chat | StrOutputParser()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
    question = state.get("original_question", "")
    memory_context = state.get("memory_context", "")

    # Token Optimization: Deduplicate retrieved chunks and bound strictly to Top 4 chunks (<1,800 tokens total)
    raw_retrieved = state.get("retrieved_context", [])
    seen_hashes = set()
    compact_retrieved = []
    total_chars = 0
    MAX_TOTAL_CHARS = 6000  # ~1,500 - 1,800 tokens ceiling
    
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
            if remaining_allowance > 400:
                # Safe newline truncate to avoid breaking markdown tables or numbers
                cut_idx = txt.rfind("\n", 0, remaining_allowance)
                if cut_idx > 200:
                    txt = txt[:cut_idx] + "\n[... Segment bounded for token efficiency ...]"
                    compact_retrieved.append(txt)
            break

        compact_retrieved.append(txt)
        total_chars += len(txt)
        if len(compact_retrieved) >= 4:
            break

    context = "\n\n---\n\n".join(compact_retrieved) if compact_retrieved else "No additional reference documents retrieved."
    document_id = state.get("document_id")

    lower_q = question.strip().lower().rstrip("!.,?")
    if not document_id:
        if lower_q in ("hi", "hello", "hey", "good morning", "good evening", "howdy", "greetings"):
            print("  [Evidence Builder: INSTANT GREETING FAST-PATH]")
            greeting_reply = (
                "Hello! 👋 I am **FinAdvisor-X**, your AI Financial Intelligence Assistant.\n\n"
                "How can I help you today? You can ask me about:\n"
                "* 📈 **Market & Stock Intelligence**: Real-time quotes, technical ratios, and company fundamentals.\n"
                "* 📄 **Document Analysis**: Upload your PDF salary slips, balance sheets, or tax returns for private isolated analysis.\n"
                "* 🧮 **Financial Calculations**: SIP compounding, DCF valuation, WACC, CAGR, and capital gains tax.\n"
                "* 🏛️ **Indian Tax & Regulatory Updates**: FY 2026-27 tax slabs (Old vs New Regime) and SEBI/RBI guidelines."
            )
            return {"draft_answer": greeting_reply, "final_answer": greeting_reply}

        if lower_q in ("market intelligence", "market", "stock intelligence", "stocks", "market & stock intelligence"):
            print("  [Evidence Builder: INSTANT MARKET INTELLIGENCE FAST-PATH]")
            market_reply = (
                "📈 **Market & Stock Intelligence Hub**\n\n"
                "I can provide real-time equity metrics, analyst targets, and company fundamentals across Indian and global markets:\n\n"
                "* 📊 **Live Quotes & Tickers**: Ask for *'Reliance price'*, *'TCS quote'*, *'NIFTY 50 status'*, or *'Apple stock price'*.\n"
                "* 🏢 **Financial Filings (10-K & Annual Reports)**: Ask *'What was Apple\\'s Services revenue in 2024?'* or *'Compare operating margins'*.\n"
                "* 🔍 **Valuation & Fundamentals**: Ask *'What is the P/E ratio and debt-to-equity of Reliance?'* or *'Explain DuPont ROE analysis'*.\n\n"
                "Type a company name or ticker to get started!"
            )
            return {"draft_answer": market_reply, "final_answer": market_reply}

        if lower_q in ("what", "help", "menu", "options", "what can you do"):
            print("  [Evidence Builder: INSTANT HELP FAST-PATH]")
            help_reply = (
                "💡 **How I Can Assist You**\n\n"
                "I am equipped with specialized financial calculation, document retrieval, and live market engines:\n\n"
                "1. **🧮 Financial Calculations**: Try *'SIP of ₹10,000 for 10 years at 12%'* or *'Calculate EMI on 50L loan for 20 years at 8.5%'*.\n"
                "2. **🏛️ Indian Tax Planning**: Try *'Tax on ₹15 Lakh income under new regime FY 2026-27'*\n"
                "3. **📈 Market Quotes**: Try *'TCS share price'* or *'Reliance market cap'*\n"
                "4. **📄 Bank Statement & PDF Ingestion**: Attach a PDF or CSV statement to analyze your monthly cash flow, savings rate, and expenses."
            )
            return {"draft_answer": help_reply, "final_answer": help_reply}

    depth = state.get("depth") or classify_depth(question)
    tool_results = state.get("draft_answer") or "None"
    chat_history = memory_context if memory_context else "None"

    try:
        print(f"  [Evidence Builder: SYNTHESIS] depth='{depth}', doc={bool(document_id)} ({len(compact_retrieved)} chunks bounded)")
        answer = builder_chain.invoke({
            "depth": depth,
            "query": question,
            "evidence_summary": context,
            "tool_results": tool_results,
            "chat_history": chat_history,
        })
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

