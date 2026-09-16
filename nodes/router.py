from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import AgentState

from core.db import chat

class Route(BaseModel):
    decision: str = Field(description="The routing decision. Must be one of: 'decompose', 'hybrid_search', 'financial_table', 'calculation', 'direct_answer'")

router_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert financial routing assistant.
    Analyze the user's question and determine the best execution path.
    - If the question asks to compare multiple distinct years/entities or has multiple distinct parts, route to 'decompose'.
    - If the question specifically asks for an arithmetic calculation (e.g., 'calculate the YoY growth', 'what is the margin'), route to 'calculation'.
    - If the question specifically asks for data that is likely found in a tabular format (e.g. balance sheet, income statement), route to 'financial_table'.
    - If the question requires looking up general text, narrative risk, or relationships from an Annual Report, route to 'hybrid_search'.
    - If the question is a simple greeting or general knowledge that doesn't require a document lookup, route to 'direct_answer'.
    """),
    ("human", "{question}")
])

router_chain = router_prompt | chat.with_structured_output(Route)

def route_question(state: AgentState):
    print("---NODE: ROUTER---")
    question = state["original_question"]
    route = router_chain.invoke({"question": question})
    print(f"Decision: {route.decision}")
    return {"routing_decision": route.decision, "current_question": question}
