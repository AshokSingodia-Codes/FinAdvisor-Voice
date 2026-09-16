from langgraph.graph import StateGraph, END
from graph.state import AgentState
from nodes.router import route_question
from nodes.decomposition import decompose_question
from nodes.retriever import retrieve_context
from nodes.evidence_builder import build_evidence
from nodes.verifier import verify_answer
from config.settings import settings

# Define graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("router", route_question)
workflow.add_node("decompose", decompose_question)
workflow.add_node("retriever", retrieve_context)
workflow.add_node("evidence_builder", build_evidence)
workflow.add_node("verifier", verify_answer)

# Set entry point
workflow.set_entry_point("router")

# Conditional edges from router
def route_decision(state: AgentState):
    decision = state["routing_decision"]
    if decision == "decompose":
        return "decompose"
    elif decision == "hybrid_search":
        return "hybrid_search"
    else:
        # direct_answer bypasses retrieval and goes straight to evidence builder
        return "direct_answer"

workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "decompose": "decompose",
        "hybrid_search": "retriever",
        "direct_answer": "evidence_builder"
    }
)

# Flow from decompose
workflow.add_edge("decompose", "retriever")

# Flow from retriever
workflow.add_edge("retriever", "evidence_builder")

# Flow from evidence builder
workflow.add_edge("evidence_builder", "verifier")

# Conditional edges from verifier (Multi-hop Iterative loop)
def check_verification(state: AgentState):
    # If verified, we are done
    if state.get("verification_passed"):
        return END
    
    # If it failed, check if we have tried too many times
    # Assuming each iteration brings ~5 chunks.
    max_chunks = settings.MAX_RETRIEVAL_ITERATIONS * 5
    if len(state.get("retrieved_context", [])) >= max_chunks:
        print("---MAX RETRIES REACHED. ENDING.---")
        return END
        
    print("---VERIFICATION FAILED. LOOPING BACK TO RETRIEVER...---")
    return "retriever"

workflow.add_conditional_edges(
    "verifier",
    check_verification,
    {
        END: END,
        "retriever": "retriever"
    }
)

# Compile the graph
app_graph = workflow.compile()
