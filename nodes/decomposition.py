from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from graph.state import AgentState

from core.db import fast_chat, get_structured_fast_chat

class SubQuery(BaseModel):
    query: str = Field(description="The standalone sub-query text.")
    strategy: str = Field(description="The retrieval strategy for this specific query: 'vector', 'graph', 'table', or 'calculation'")

class SubQueries(BaseModel):
    queries: List[SubQuery] = Field(description="List of distinct standalone sub-queries.")

decompose_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert financial assistant.
    Your task is to break down a complex user question into a list of simpler, distinct sub-queries that can be independently searched.
    For example, "Compare Apple's 2023 and 2024 CapEx" should become ["What was Apple's 2023 CapEx?", "What was Apple's 2024 CapEx?"].
    """),
    ("human", "{question}")
])

decompose_chain = decompose_prompt | get_structured_fast_chat(SubQueries)

def decompose_question(state: AgentState):
    print("---NODE: DECOMPOSITION---")
    question = state["original_question"]
    sub_queries = decompose_chain.invoke({"question": question})
    
    # Extract just the text queries for the retriever for now
    query_texts = [sq.query for sq in sub_queries.queries]
    
    print(f"Decomposed into {len(query_texts)} queries: {query_texts}")
    return {"decomposed_questions": query_texts}
