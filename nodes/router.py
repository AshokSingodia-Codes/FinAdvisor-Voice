from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.state import AgentState
from core.db import fast_chat, get_structured_fast_chat

class Route(BaseModel):
    decision: str = Field(description="The routing decision. Must be one of: 'decompose', 'hybrid_search', 'financial_table', 'calculation', 'math_calculation', 'direct_answer', 'live_market_data'")

router_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert financial routing assistant.
    Analyze the user's question along with the recent conversation history to determine the best execution path.
    - If the question asks to compare multiple distinct years/entities or has multiple distinct parts, route to 'decompose'.
    - If the question contains digits AND one of these keywords (add, subtract, sum, total, difference, multiply, divide, plus, minus) for simple arithmetic, route to 'math_calculation'.
    - If the question asks to COMPUTE or CALCULATE a specific numerical result using a financial formula with given numbers (e.g. 'Calculate WACC given equity of...', 'Compute CAGR if investment grew from 10k to 25k', 'What is the future value of ₹5000/mo SIP at 12%?'), asks about an investment growing/losing over time (compound interest calculation), percentage change with numbers, or what X% of Y is, route to 'calculation'.
    - If the question asks for the DEFINITION, EXPLANATION, or CONCEPTUAL FORMULA from textbooks/filings (e.g. 'What is the formula for WACC?', 'How is Free Cash Flow defined?', 'Explain DuPont analysis formula'), route to 'hybrid_search'.
    - If the question specifically asks for data that is likely found in a tabular format (e.g. balance sheet, income statement line items), route to 'financial_table'.
    - If the question requires looking up general text, narrative risk, financial definitions, or relationships from an Annual Report or finance literature, route to 'hybrid_search'.
    - If the question or conversation refers to live stock prices, current market data, real-time ticker information, recent news of a stock, or explicitly mentions Indian indices (e.g., NIFTY 50, SENSEX) or Indian stocks (e.g. TCS, Reliance), route to 'live_market_data'.
    - If the question is a conversational follow-up, advice question, personal financial detail lookup/memory query ("what was my income", "how much do I earn", "my expenses"), general knowledge, portfolio analysis, or greeting, route to 'direct_answer'.
    - If the user has attached a personal document and the question is about their own financial data (salary, expenses, statement, balance, etc.), route to 'hybrid_search' so their document is searched.
    """),
    ("human", """{memory_context}

Current Question: {question}""")
])

router_chain = router_prompt | get_structured_fast_chat(Route)

def format_history_for_router(history, max_turns=4):
    if not history:
        return "None (First interaction)"
    formatted = []
    for msg in history[-max_turns:]:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "").strip()
        if len(content) > 300:
            content = content[:300] + "..."
        formatted.append(f"{role}: {content}")
    return "\n".join(formatted)

def route_question(state: AgentState):
    print("---NODE: ROUTER---")
    question = state.get("original_question", "")
    memory_context = state.get("memory_context", "")
    document_id = state.get("document_id")
    lower = question.strip().lower()

    # --- Fast-Path 1: Instant Personal Document Route (<1ms) ---
    if document_id:
        has_digits = any(char.isdigit() for char in lower)
        is_explicit_math = has_digits and any(term in lower for term in ["add", "subtract", "multiply", "divide", "plus", "minus", "sum", "total", "cagr", "sip", "wacc", "npv", "dcf", "emi"])
        if not is_explicit_math:
            print("  [Router: FAST-PATH PERSONAL DOC] -> 'hybrid_search'")
            return {"routing_decision": "hybrid_search", "current_question": question}

    # --- Fast-Path 2: Instant Greetings / Casual Chit-Chat (<1ms) ---
    if lower in ("hi", "hello", "hey", "good morning", "good evening", "how are you", "who are you", "help"):
        print("  [Router: FAST-PATH CHIT-CHAT] -> 'direct_answer'")
        return {"routing_decision": "direct_answer", "current_question": question}

    # --- Fast-Path 3: Instant Live Market Tickers (<1ms) ---
    if any(term in lower for term in ["reliance", "tcs", "hdfc", "nifty", "sensex", "infosys", "itc", "live price", "ticker"]):
        print("  [Router: FAST-PATH LIVE MARKET] -> 'live_market_data'")
        return {"routing_decision": "live_market_data", "current_question": question}

    # --- Fast-Path 4: Instant Arithmetic (<1ms) ---
    has_digits = any(char.isdigit() for char in lower)
    if has_digits and any(op in lower for op in ["+", "-", "*", "/", "add ", "subtract ", "multiply ", "plus ", "minus "]):
        print("  [Router: FAST-PATH ARITHMETIC] -> 'math_calculation'")
        return {"routing_decision": "math_calculation", "current_question": question}

    try:
        route = router_chain.invoke({
            "question": question,
            "memory_context": memory_context
        })
        decision = route.decision
    except Exception as e:
        print(f"Router fallback due to: {e}")
        is_calculation_query = any(term in lower for term in ["calculate", "compute", "how much is", "what is the return on"])
        
        if any(term in lower for term in ["reliance", "tcs", "hdfc", "nifty", "sensex", "stock", "price"]):
            decision = "live_market_data"
        elif has_digits and any(term in lower for term in ["add", "subtract", "multiply", "divide", "plus", "minus"]):
            decision = "math_calculation"
        elif has_digits and is_calculation_query and any(term in lower for term in ["wacc", "npv", "cagr", "dcf", "yoy", "growth", "margin", "interest", "sip", "emi", "irr"]):
            decision = "calculation"
        elif any(term in lower for term in ["what is", "define", "explain", "how does", "formula for", "definition"]):
            decision = "hybrid_search"
        elif any(term in lower for term in ["wacc", "npv", "cagr", "dcf", "yoy", "growth", "margin"]):
            decision = "calculation"
        else:
            decision = "direct_answer"

    # -------------------------------------------------------------------------
    # DOCUMENT MODE OVERRIDE
    # When a personal document is attached, every question about the document
    # must pass through the retriever (exclusive personal-doc path).
    # Only queries with explicit digits AND math keywords are sent to math solver.
    # -------------------------------------------------------------------------
    document_id = state.get("document_id")
    if document_id:
        lower = question.lower()
        has_digits = any(char.isdigit() for char in lower)
        is_explicit_math = has_digits and any(term in lower for term in ["add", "subtract", "multiply", "divide", "plus", "minus", "sum", "total", "cagr", "sip", "wacc", "npv", "dcf", "emi"])
        if not is_explicit_math:
            print(f"  [Router: DOCUMENT MODE] overriding '{decision}' → 'hybrid_search'")
            decision = "hybrid_search"

    print(f"Decision: {decision}")
    return {"routing_decision": decision, "current_question": question}

