from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.state import AgentState
from core.db import chat, get_structured_chat

class Route(BaseModel):
    decision: str = Field(description="The routing decision. Must be one of: 'decompose', 'hybrid_search', 'financial_table', 'calculation', 'math_calculation', 'direct_answer', 'live_market_data'")

router_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert financial routing assistant.
    Analyze the user's question along with the recent conversation history to determine the best execution path.
    - If the question asks to compare multiple distinct years/entities or has multiple distinct parts, route to 'decompose'.
    - If the question contains digits AND one of these keywords (add, subtract, sum, total, difference, multiply, divide, plus, minus) for simple arithmetic, route to 'math_calculation'.
    - If the question asks for ANY financial formula (e.g., 'YoY growth', 'margin', 'NPV', 'DCF', 'WACC'), asks about an investment growing/losing over time (compound interest), percentage change, or what X% of Y is, route to 'calculation'.
    - If the question specifically asks for data that is likely found in a tabular format (e.g. balance sheet, income statement), route to 'financial_table'.
    - If the question requires looking up general text, narrative risk, or relationships from an Annual Report, route to 'hybrid_search'.
    - If the question or conversation refers to live stock prices, current market data, real-time ticker information, recent news of a stock, or explicitly mentions Indian indices (e.g., NIFTY 50, SENSEX) or Indian stocks (e.g. TCS, Reliance), route to 'live_market_data'.
    - If the question is a conversational follow-up, advice question, personal financial detail lookup/memory query ("what was my income", "how much do I earn", "my expenses"), general knowledge, portfolio analysis, or greeting, route to 'direct_answer'.
    """),
    ("human", """{memory_context}

Current Question: {question}""")
])

router_chain = router_prompt | get_structured_chat(Route)

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
    
    try:
        route = router_chain.invoke({
            "question": question,
            "memory_context": memory_context
        })
        decision = route.decision
    except Exception as e:
        print(f"Router fallback due to: {e}")
        lower = question.lower()
        if any(term in lower for term in ["reliance", "tcs", "hdfc", "nifty", "sensex", "stock", "price"]):
            decision = "live_market_data"
        elif any(term in lower for term in ["wacc", "npv", "cagr", "dcf", "yoy", "growth", "margin"]):
            decision = "calculation"
        elif any(term in lower for term in ["add", "subtract", "multiply", "divide", "sum"]):
            decision = "math_calculation"
        else:
            decision = "direct_answer"

    print(f"Decision: {decision}")
    return {"routing_decision": decision, "current_question": question}
