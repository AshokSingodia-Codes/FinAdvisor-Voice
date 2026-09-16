from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.state import AgentState
from core.db import chat

class Verification(BaseModel):
    is_supported: bool = Field(description="True if the draft answer is fully supported by the context.")
    numerical_consistency: bool = Field(description="True if all numbers in the draft exactly match the context.")
    citation_consistency: bool = Field(description="True if the draft properly cites its sources (e.g. Page X, Table Y).")
    reasoning: str = Field(description="Brief explanation of why it is or isn't supported.")

verifier_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert fact-checker and financial auditor.
    Your job is to read a draft answer and the original context documents.
    1. CLAIM GROUNDING: If the draft claims facts NOT in the context, return is_supported=False.
    2. NUMERICAL CONSISTENCY: Verify every single number in the draft. If it doesn't match the text exactly, return numerical_consistency=False.
    3. CITATIONS: Check if the draft provides provenance (where it got the info). If not, return citation_consistency=False.
    4. If the draft answer explicitly says it does not have enough information, return is_supported=False.
    """),
    ("human", "Context:\n{context}\n\nDraft Answer:\n{draft}\n\nQuestion:\n{question}")
])

verifier_chain = verifier_prompt | chat.with_structured_output(Verification)

def verify_answer(state: AgentState):
    print("---NODE: VERIFIER---")
    question = state["original_question"]
    draft = state["draft_answer"]
    context = "\n\n---\n\n".join(state.get("retrieved_context", []))
    draft = state["draft_answer"]
    
    verification = verifier_chain.invoke({
        "context": context,
        "draft": draft,
        "question": question
    })
    
    # Strict verification requires all three to pass
    strict_pass = verification.is_supported and verification.numerical_consistency
    
    print(f"Verification Passed? {strict_pass} (Supported: {verification.is_supported}, Numbers Match: {verification.numerical_consistency}) - {verification.reasoning}")
    
    # If passed, it becomes the final answer.
    final_answer = draft if strict_pass else ""
    
    return {
        "verification_passed": strict_pass,
        "final_answer": final_answer
    }
