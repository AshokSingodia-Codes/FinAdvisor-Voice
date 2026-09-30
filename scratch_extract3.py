import time
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from core.db import get_structured_synthesis_chat
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j setup
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USERNAME", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))
driver = GraphDatabase.driver(URI, auth=AUTH)

# Define schema models
class ExtractedEntity(BaseModel):
    name: str = Field(description="The canonical name of the entity.")
    type: str = Field(description="The type (Company, Segment, RiskFactor, Concept, Metric, DocumentChunk).")
    
class ExtractedRelationship(BaseModel):
    source_entity: str = Field(description="Exact name of the source entity.")
    target_entity: str = Field(description="Exact name of the target entity.")
    relationship: str = Field(description="Relationship (HAS_SEGMENT, FACES_RISK, REPORTED_METRIC, DRIVES_METRIC, DEPENDS_ON, MENTIONED_IN).")
    properties: Optional[dict] = Field(description="Optional properties for the edge, e.g., value, period, unit for metrics.")

class ExtractionResult(BaseModel):
    entities: List[ExtractedEntity]
    relationships: List[ExtractedRelationship]

chunks = [
    {
        "id": "chunk_A",
        "text": "[CHUNK_ID: chunk_A] Apple Inc. reported Q1 net sales for the iPhone segment of $65B. The iPhone segment continues to perform well."
    },
    {
        "id": "chunk_B",
        "text": "[CHUNK_ID: chunk_B] In Q2, Apple's iPhone revenue was $55 billion. The company (Apple Inc.) sees strong demand."
    },
    {
        "id": "chunk_C",
        "text": "[CHUNK_ID: chunk_C] For the full year, iPhone segment net sales totaled $200B at Apple Inc."
    }
]

def run_extraction_and_merge():
    print("Starting Multi-Chunk Deduplication & MERGE test...")
    llm = get_structured_synthesis_chat(ExtractionResult)
    
    all_entities = []
    all_rels = []
    
    # 1. Extraction
    for chunk in chunks:
        prompt = f"""
        You are an expert financial knowledge extractor. 
        Extract entities and relationships from the following text based on this strict schema.
        
        Allowed Entity Types: Company, Segment, RiskFactor, Concept, Metric, DocumentChunk
        Allowed Relationships: HAS_SEGMENT, FACES_RISK, REPORTED_METRIC, DRIVES_METRIC, DEPENDS_ON, MENTIONED_IN
        
        CRITICAL INSTRUCTIONS:
        1. Only extract entities that fit exactly into the Allowed Entity Types. Discard locations, people, arbitrary nouns.
        2. The chunk ID is provided in brackets at the top. You MUST extract a DocumentChunk entity for it, and link EVERY OTHER extracted entity to this DocumentChunk using the MENTIONED_IN relationship.
        3. For metrics, include properties on the REPORTED_METRIC or DRIVES_METRIC edge to capture the value, period, and unit.
        4. CANONICALIZATION RULE FOR METRICS: Extract base metric names ONLY (e.g., "revenue", "operating income"). DO NOT include the segment or company name in the metric name. Map "net sales" to "revenue". Lowercase all metric names.
        5. CANONICALIZATION RULE FOR COMPANIES: Always output "Apple Inc." if Apple is mentioned.
        6. CANONICALIZATION RULE FOR SEGMENTS: Always output "iPhone" if the iPhone segment is mentioned.
        
        Text:
        {chunk['text']}
        """
        result = llm.invoke(prompt)
        # Handle parsed pydantic object
        if hasattr(result, 'entities'):
            all_entities.extend([e.model_dump() for e in result.entities])
            all_rels.extend([r.model_dump() for r in result.relationships])
        else:
            print(f"Failed to parse result for {chunk['id']}")
            
    print(f"Extracted {len(all_entities)} entities and {len(all_rels)} relationships across 3 chunks.")
    
    # 2. Cleanup Neo4j before test
    with driver.session() as session:
        session.run("MATCH (n:Company) DETACH DELETE n")
        session.run("MATCH (n:Segment) DETACH DELETE n")
        session.run("MATCH (n:Metric) DETACH DELETE n")
        session.run("MATCH (n:DocumentChunk) DETACH DELETE n")
        
    # 3. MERGE Ingestion
    with driver.session() as session:
        for ent in all_entities:
            # Upsert entity node with MERGE
            cypher = f"""
            MERGE (n:`{ent['type']}` {{name: $name}})
            """
            session.run(cypher, name=ent['name'])
            
        for rel in all_rels:
            # We don't know the exact types of source/target, so we just MATCH by name.
            # In a real ingest, we'd know or store the types. For now, match any node with the name.
            cypher = f"""
            MATCH (src {{name: $source}})
            MATCH (tgt {{name: $target}})
            MERGE (src)-[r:`{rel['relationship']}`]->(tgt)
            SET r += $props
            """
            props = rel.get('properties') or {}
            session.run(cypher, source=rel['source_entity'], target=rel['target_entity'], props=props)
            
    # 4. Verify Deduplication
    with driver.session() as session:
        company_count = session.run("MATCH (c:Company) RETURN count(c) as cnt").single()['cnt']
        segment_count = session.run("MATCH (s:Segment) RETURN count(s) as cnt").single()['cnt']
        metric_count = session.run("MATCH (m:Metric) RETURN count(m) as cnt").single()['cnt']
        
        print("\n=== NEO4J FINAL COUNTS ===")
        print(f"Company nodes: {company_count}")
        print(f"Segment nodes: {segment_count}")
        print(f"Metric nodes: {metric_count}")
        
        # Print metrics to show it's unified to "revenue"
        metrics = session.run("MATCH (m:Metric) RETURN m.name as name").data()
        print(f"Metric names: {[m['name'] for m in metrics]}")
        
        # Check DRIVES_METRIC edges
        edges = session.run("MATCH (s:Segment)-[r:DRIVES_METRIC]->(m:Metric) RETURN s.name, r, m.name").data()
        print(f"DRIVES_METRIC edges: {len(edges)}")
        for e in edges:
            print(e)
            
    driver.close()

if __name__ == "__main__":
    run_extraction_and_merge()
