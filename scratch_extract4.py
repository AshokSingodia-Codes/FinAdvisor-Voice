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
    type: str = Field(description="The type (Company, Segment, RiskFactor, Concept, Metric, Chunk).")
    
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
        "id": "chunk_FY22",
        "text": "[CHUNK_ID: chunk_FY22] In FY22, Apple's iPhone segment generated $205 billion in revenue."
    },
    {
        "id": "chunk_FY23",
        "text": "[CHUNK_ID: chunk_FY23] For FY23, the iPhone segment saw a slight dip, reporting $200 billion in net sales."
    },
    {
        "id": "chunk_FY24",
        "text": "[CHUNK_ID: chunk_FY24] Apple reported that iPhone revenue recovered in FY24, reaching $210 billion."
    }
]

from langchain_google_genai import ChatGoogleGenerativeAI
def run_extraction_and_merge():
    print("Starting Multi-Period Deduplication & Time-Series Test...")
    
    # MOCK the extracted entities to bypass LLM rate limits.
    # This precisely represents what the extraction prompt produces.
    all_entities = [
        # Chunk A
        {"name": "chunk_FY22", "type": "Chunk"},
        {"name": "Apple Inc.", "type": "Company"},
        {"name": "iPhone", "type": "Segment"},
        {"name": "revenue", "type": "Metric"},
        
        # Chunk B
        {"name": "chunk_FY23", "type": "Chunk"},
        {"name": "Apple Inc.", "type": "Company"},
        {"name": "iPhone", "type": "Segment"},
        {"name": "revenue", "type": "Metric"},
        
        # Chunk C
        {"name": "chunk_FY24", "type": "Chunk"},
        {"name": "Apple Inc.", "type": "Company"},
        {"name": "iPhone", "type": "Segment"},
        {"name": "revenue", "type": "Metric"}
    ]
    
    all_rels = [
        # Chunk A
        {"source_entity": "Apple Inc.", "target_entity": "iPhone", "relationship": "HAS_SEGMENT"},
        {"source_entity": "iPhone", "target_entity": "revenue", "relationship": "REPORTED_METRIC", "properties": {"value": 205, "unit": "billion USD", "period": "FY22"}},
        
        # Chunk B
        {"source_entity": "Apple Inc.", "target_entity": "iPhone", "relationship": "HAS_SEGMENT"},
        {"source_entity": "iPhone", "target_entity": "revenue", "relationship": "REPORTED_METRIC", "properties": {"value": 200, "unit": "billion USD", "period": "FY23"}},
        
        # Chunk C
        {"source_entity": "Apple Inc.", "target_entity": "iPhone", "relationship": "HAS_SEGMENT"},
        {"source_entity": "iPhone", "target_entity": "revenue", "relationship": "REPORTED_METRIC", "properties": {"value": 210, "unit": "billion USD", "period": "FY24"}},
    ]
    
    print(f"Mocked {len(all_entities)} entities and {len(all_rels)} relationships across 3 chunks.")
    
    # 2. Cleanup Neo4j before test
    with driver.session() as session:
        session.run("MATCH (n:Company) DETACH DELETE n")
        session.run("MATCH (n:Segment) DETACH DELETE n")
        session.run("MATCH (n:Metric) DETACH DELETE n")
        session.run("MATCH (n:Chunk) DETACH DELETE n")
        
    # 3. MERGE Ingestion
    with driver.session() as session:
        for ent in all_entities:
            # Upsert entity node with MERGE
            cypher = f"MERGE (n:`{ent['type']}` {{name: $name}})"
            session.run(cypher, name=ent['name'])
            
        for rel in all_rels:
            props = rel.get('properties') or {}
            period = props.get('period')
            
            # The CRITICAL fix: include period in the MERGE match pattern if it exists!
            if period:
                cypher = f"""
                MATCH (src {{name: $source}})
                MATCH (tgt {{target_name: $target}})
                MERGE (src)-[r:`{rel['relationship']}` {{period: $period}}]->(tgt)
                SET r += $props
                """
                # wait, small bug in target_name
                cypher = cypher.replace("target_name", "name")
                session.run(cypher, source=rel['source_entity'], target=rel['target_entity'], period=period, props=props)
            else:
                cypher = f"""
                MATCH (src {{name: $source}})
                MATCH (tgt {{name: $target}})
                MERGE (src)-[r:`{rel['relationship']}`]->(tgt)
                SET r += $props
                """
                session.run(cypher, source=rel['source_entity'], target=rel['target_entity'], props=props)
            
    # 4. Verify Multi-Period Correctness
    with driver.session() as session:
        metric_count = session.run("MATCH (m:Metric) RETURN count(m) as cnt").single()['cnt']
        print(f"\nMetric nodes: {metric_count} (Should be 1)")
        
        # Check DRIVES_METRIC / REPORTED_METRIC edges
        edges = session.run("MATCH (s)-[r:DRIVES_METRIC|REPORTED_METRIC]->(m:Metric) WHERE s.name = 'iPhone' RETURN r.period as period, r.value as value ORDER BY period").data()
        print(f"iPhone -> revenue edges: {len(edges)}")
        for e in edges:
            print(f"  Period: {e['period']} | Value: {e['value']}")
            
    driver.close()

if __name__ == "__main__":
    run_extraction_and_merge()
