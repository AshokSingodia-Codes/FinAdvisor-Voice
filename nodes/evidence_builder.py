from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from graph.state import AgentState
from core.db import chat

builder_prompt = ChatPromptTemplate.from_template("""
You are an expert financial analyst. 
Answer the following question based ONLY on the provided context.

Context:
{context}

Question: {question}

If the context does not contain the answer, say "I don't have enough information to answer that."
Answer:
""")

builder_chain = builder_prompt | chat | StrOutputParser()

def build_evidence(state: AgentState):
    print("---NODE: EVIDENCE BUILDER (DRAFTING ANSWER)---")
    question = state["original_question"]
    context = "\n\n---\n\n".join(state.get("retrieved_context", []))
    
    draft = builder_chain.invoke({"context": context, "question": question})
    print("Draft Answer generated.")
    return {"draft_answer": draft}
