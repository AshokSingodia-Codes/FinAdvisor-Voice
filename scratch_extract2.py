import time
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from core.db import get_structured_synthesis_chat

# Define schema models based on the approved plan
class ExtractedEntity(BaseModel):
    name: str = Field(description="The exact name of the entity.")
    type: str = Field(description="The type of the entity (Company, Segment, RiskFactor, Concept, Metric).")
    
class ExtractedRelationship(BaseModel):
    source_entity: str = Field(description="The exact name of the source entity.")
    target_entity: str = Field(description="The exact name of the target entity.")
    relationship: str = Field(description="Relationship type (HAS_SEGMENT, FACES_RISK, REPORTED_METRIC, DRIVES_METRIC, DEPENDS_ON, MENTIONED_IN).")
    properties: Optional[dict] = Field(description="Optional properties for the edge, e.g., value, period, unit for metrics.")

class ExtractionResult(BaseModel):
    entities: List[ExtractedEntity]
    relationships: List[ExtractedRelationship]

# Sample text with financial figures and a mock chunk ID
sample_text = """
[CHUNK_ID: chunk_9942_FY23]
Apple Inc. reported total net sales of $383.29 billion for the fiscal year ended September 30, 2023. 
The iPhone segment was the largest contributor, generating $200.58 billion in revenue, driven by strong demand in emerging markets. 
Meanwhile, the Services segment drove $85.20 billion in revenue, reflecting a shift in the Company's business model.
"""

from langchain_groq import ChatGroq
import os

def run_extraction():
    print("Starting Metric + Citation extraction test...")
    start_time = time.time()
    
    # We use the structured synthesis chat for offline extraction
    llm = get_structured_synthesis_chat(ExtractionResult)
    
    prompt = f"""
    You are an expert financial knowledge extractor. 
    Extract entities and relationships from the following text based on this strict schema.
    
    Allowed Entity Types: Company, Segment, RiskFactor, Concept, Metric, DocumentChunk
    Allowed Relationships: HAS_SEGMENT, FACES_RISK, REPORTED_METRIC, DRIVES_METRIC, DEPENDS_ON, MENTIONED_IN
    
    CRITICAL INSTRUCTIONS:
    1. Only extract entities that fit exactly into the Allowed Entity Types. Do NOT extract locations, people, or arbitrary nouns. Discard them.
    2. The chunk ID is provided in brackets at the top. You MUST extract a DocumentChunk entity for it, and link EVERY OTHER extracted entity to this DocumentChunk using the MENTIONED_IN relationship.
    3. For metrics (e.g. revenue, net sales), include properties on the REPORTED_METRIC or DRIVES_METRIC edge to capture the value, period, and unit.
    
    Text:
    {sample_text}
    """
    
    result = llm.invoke(prompt)
    end_time = time.time()
    
    print(f"Extraction completed in {end_time - start_time:.2f} seconds.")
    print("=== EXTRACTED DATA ===")
    if hasattr(result, "content"):
        print(result.content)
    else:
        print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    run_extraction()
