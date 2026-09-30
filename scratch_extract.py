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
    relationship: str = Field(description="Relationship type (HAS_SEGMENT, FACES_RISK, DRIVES_METRIC, RELATED_TO).")

class ExtractionResult(BaseModel):
    entities: List[ExtractedEntity]
    relationships: List[ExtractedRelationship]

# Sample text from a standard 10-K risk factor / business section
sample_text = """
Apple Inc. manages its business primarily on a geographic basis. The Company's reportable operating segments consist of the Americas, Europe, Greater China, Japan and Rest of Asia Pacific.
Although the Company is headquartered in the United States, it derives a majority of its revenue from international sales. Therefore, the Company faces significant Foreign Currency Fluctuation risk, as well as Supply Chain Disruption risks in the Greater China segment.
"""

def run_extraction():
    print("Starting small-sample extraction test...")
    start_time = time.time()
    
    # We use the structured synthesis chat for offline extraction
    llm = get_structured_synthesis_chat(ExtractionResult)
    
    prompt = f"""
    You are an expert financial knowledge extractor. 
    Extract entities and relationships from the following text based on this strict schema:
    
    Allowed Entity Types: Company, Segment, RiskFactor, Concept, Metric
    Allowed Relationships: HAS_SEGMENT, FACES_RISK, DRIVES_METRIC, RELATED_TO
    
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
