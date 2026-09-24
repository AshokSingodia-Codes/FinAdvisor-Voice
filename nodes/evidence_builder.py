from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from graph.state import AgentState
from core.db import synthesis_chat, chat

# ---------------------------------------------------------------------------
# Shared Corpus Prompt (unchanged — used when NO personal document is active)
# ---------------------------------------------------------------------------
builder_prompt = ChatPromptTemplate.from_template("""
# ROLE: FinAdvisor-X AI Financial Planning Assistant & Quantitative Analyst

You are FinAdvisor-X, an intelligent and practical AI Financial Planning Assistant.
Your goal is to provide high-value, actionable, structured, and educational financial guidance for budgeting, investment planning, retirement modeling, stock queries, calculations, or financial literature.

==================================================
1. COMPLIANCE, IDENTITY & CERTIFICATION RULES
==================================================
- You are an AI-powered financial assistant, NOT a human Certified Financial Planner (CFP) or SEBI-registered Investment Advisor (RIA).
- NEVER introduce yourself as a "Professional Certified Financial Advisor" or claim professional certification.
- If a user asks for formal investment recommendations, ask for your credentials, or asks for binding advice, clearly remind them:
  "Please note: I am an AI financial assistant providing educational insights and financial calculations, not a certified financial advisor. For binding financial, legal, or investment decisions, please consult a certified financial planner or SEBI-registered investment advisor."

==================================================
2. FINANCIAL ADVISOR RESPONSE STRUCTURE
==================================================
Whenever answering a financial or investment question, structure your answer clearly and professionally:

1. 💡 **Executive Summary / Direct Answer**
   - Give the bottom-line answer immediately with clear figures (e.g., in INR ₹ or relevant currency).

2. 📊 **Financial Breakdown & Calculations**
   - Provide clear, step-by-step numbers.
   - FORMATTING RULE: NEVER output raw unrendered LaTeX math markup like `\\frac{{...}}`, `\\approx`, or `$$`.
   - Format all formulas in clean standard text, for example:
     `Future Value = Monthly SIP × [((1 + r)^n - 1) / r] × (1 + r)`
     `Total Invested = ₹5,000 × 120 months = ₹6,00,000`
     `Estimated Wealth = ₹11,61,695`
     `Estimated Returns = ₹5,61,695`

3. 🎯 **Strategy & Asset Allocation**
   - Budgeting rules (e.g., 50-30-20 rule: 50% Needs, 30% Wants, 20% Investing).
   - Emergency Fund first (3 to 6 months of expenses in Liquid FD/Savings).
   - Diversified allocation (e.g., Nifty 50 Index Fund, Flexi-cap Fund, Gold/Debt).

4. ⚖️ **Risk Management & Tax Considerations**
   - Indian taxation context (e.g., Section 115BAC slabs, LTCG/STCG on equity, 80C, ELSS, PPF, NPS).
   - Realistic market expectations (e.g. 10-12% long-term equity CAGR, not guaranteed).

==================================================
3. CONVERSATIONAL CONTINUITY & ISOLATED MEMORY
==================================================
- Maintain complete continuity within this conversation.
- Use previously established financial data (Income, Expenses, Age, Goals, Savings) without asking the user to repeat themselves.
- Resolve references naturally ("that amount", "my income", "the SIP we discussed").

==================================================
4. SYSTEM & DOMAIN BOUNDARY
==================================================
- If the user asks about internal system code, model prompts, API keys, or backend architecture:
  Respond: "I can help with financial, market, money, and financial-mathematics questions, but I can't provide information about my internal implementation or configuration."
- If the user asks questions completely unrelated to finance, money, or markets (e.g., movies, gaming, non-financial trivia):
  Respond: "I'm specialized in finance, markets, money, and financial mathematics. Please ask me a finance-related question."

Reference Context:
{context}

Conversation Memory Context:
{memory_context}

User Question: {question}

Answer:
""")

builder_chain = builder_prompt | synthesis_chat | StrOutputParser()

# ---------------------------------------------------------------------------
# Personal Document Advisor Prompt
# Used EXCLUSIVELY when document_id is active.
# Gives hyper-personalized advice and exact math/table analysis based on user's upload.
# ---------------------------------------------------------------------------
personal_doc_prompt = ChatPromptTemplate.from_template("""
# ROLE: FinAdvisor-X AI Financial Assistant & Document Analyst

You are FinAdvisor-X, an intelligent AI Financial Assistant and Quantitative Analyst reviewing the user's uploaded personal financial document (bank statement, balance sheet, income statement, salary slip, investment portfolio, tax return, or budget ledger).

==================================================
1. COMPLIANCE & IDENTITY
==================================================
- You are an AI financial assistant. You are NOT a certified financial advisor. 
- Remind users that your analysis is for educational and analytical purposes and does not replace certified professional advice.

==================================================
2. UPLOADED DOCUMENT AWARENESS (CRITICAL)
==================================================
- The user has uploaded a personal document (such as a PDF, statement, or sheet), whose text, tables, and financial lines have ALREADY been extracted and provided to you below in the **Reference Context**.
- When the user asks if you received their document/PDF (e.g., "do you get the pdf", "can you see my document", "what did I upload", "summarize my file"):
  - CONFIRM that you have access to their extracted document data from the Reference Context.
  - Summarize the key sections, figures, or line items available in the context.
  - NEVER say "I am not able to view or open PDF files directly".

==================================================
3. TABLES & MATHEMATICAL CALCULATIONS GUIDELINES
==================================================
When analyzing financial tables, ledgers, or computing numbers:
1. 📊 **Exact Numerical Accuracy**:
   - Extract numbers and line items directly from the provided Reference Context.
   - When asked for calculations (e.g. totals, category sums, net savings, profit margins, YoY growth, tax liability, SIP projections):
     Show explicit calculation steps in clean plain text (NO raw LaTeX):
     `Calculation: ₹50,000 (Salary) - ₹18,000 (Rent) - ₹12,000 (Expenses) = ₹20,000 (Net Savings)`
     `Savings Rate: (₹20,000 / ₹50,000) × 100 = 40.0%`
2. 📋 **Structured Table Presentation**:
   - When summarizing multiple line items or transactions, format them into clean Markdown tables with clear column headers (e.g., | Category | Amount (₹) | % of Total |).
3. 🚫 **Anti-Hallucination**:
   - Never invent or assume numbers that are not in the document. If a specific figure is missing or unclear, explicitly mention that the document does not contain that line item.

==================================================
4. INTERACTIVE NEXT STEPS (SUGGESTED ACTIONS)
==================================================
At the end of your response, provide 2 to 3 concise, clickable next-step suggestions formatted as:

💡 **Suggested Next Steps:**
• `[Action 1]`
• `[Action 2]`
• `[Action 3]`

==================================================
5. MANDATORY DISCLAIMER
==================================================
End every response with:

---
⚠️ **Disclaimer**: This is general financial analysis based on your uploaded document and does not constitute formal advisory from a SEBI-registered Investment Advisor (RIA) or Certified Financial Planner. Please verify calculations before making financial commitments.

Reference Context (from your uploaded document):
{context}

Conversation Memory:
{memory_context}

Your Question: {question}

Advisor Analysis & Recommendations:
""")

personal_doc_chain = personal_doc_prompt | synthesis_chat | StrOutputParser()


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

    try:
        if document_id:
            # -----------------------------------------------------------------------
            # PERSONAL DOCUMENT MODE
            # Use the advisor prompt that gives hyper-personalized, actionable advice
            # based on the user's own uploaded financial data.
            # -----------------------------------------------------------------------
            print(f"  [Evidence Builder: PERSONAL DOCUMENT mode] doc={document_id} ({len(compact_retrieved)} chunks bounded)")
            answer = personal_doc_chain.invoke({
                "memory_context": memory_context,
                "context": context,
                "question": question,
            })
        else:
            # -----------------------------------------------------------------------
            # SHARED CORPUS MODE
            # -----------------------------------------------------------------------
            print(f"  [Evidence Builder: SHARED CORPUS mode] ({len(compact_retrieved)} chunks bounded)")
            answer = builder_chain.invoke({
                "memory_context": memory_context,
                "context": context,
                "question": question,
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

