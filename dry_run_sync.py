import os
import json
import concurrent.futures
from neo4j import GraphDatabase
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
MODEL_STRING = "qwen/qwen3.8-27b"
llm_raw = ChatGroq(model_name=MODEL_STRING, temperature=0, max_tokens=4000, api_key=os.environ["GROQ_API_KEY"])

class ExtractedEntity(BaseModel):
    name: str = Field(description="Name of the entity.")
    type: str = Field(description="Type of the entity. Must be EXACTLY one of: Company, Segment, RiskFactor, Concept, Metric.")

class ExtractedRelationship(BaseModel):
    source: str = Field(description="Source entity name.")
    target: str = Field(description="Target entity name.")
    type: str = Field(description="Type of the relationship.")
    properties: dict = Field(description="Key-value pairs for properties. MUST include 'period' for financial metrics (e.g. 'FY24').", default_factory=dict)

class ExtractionOutput(BaseModel):
    entities: List[ExtractedEntity]
    relationships: List[ExtractedRelationship]

llm = llm_raw.with_structured_output(ExtractionOutput)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
def extract_chunk(chunk):
    chunk_id = chunk["id"]
    text = chunk["text"]
    
    prompt = f"""
    Extract entities and relationships from this text.
    Entities must be one of: Company, Segment, RiskFactor, Concept, Metric. Discard any entity that does not fit perfectly into one of these types. Do NOT force-fit geographical locations like "United States" into Concept or Location. Discard them.
    Financial metrics MUST include a 'period' property in their relationships (e.g., 'period': 'FY23') so that multi-year data does not overwrite itself.

    [CHUNK_ID: {chunk_id}]
    {text}
    """
    try:
        result = llm.invoke(prompt)
        # Using model_dump instead of dict to avoid deprecation warning
        if hasattr(result, 'entities'):
            return {"id": chunk_id, "entities": [e.model_dump() for e in result.entities], "relationships": [r.model_dump() for r in result.relationships]}
    except Exception as e:
        print(f"Failed extraction for {chunk_id}: {e}")
        raise e
    return {"id": chunk_id, "entities": [], "relationships": []}

def main():
    print(f"Starting SYNC Dry Run with 50 real chunks using model: {MODEL_STRING}")
    
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    # Fetch 10 chunks to avoid extreme rate limits
    with driver.session() as session:
        res = session.run("MATCH (c:Chunk) RETURN c.id as id, c.text as text LIMIT 10")
        chunks = [{"id": r["id"], "text": r["text"]} for r in res]
    driver.close()
    
    print(f"Fetched {len(chunks)} chunks from Vector index.")
    
    results = []
    # Process synchronously using ThreadPoolExecutor (max_workers=5 to avoid 429 too fast)
    print(f"Processing {len(chunks)} chunks...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(extract_chunk, chunk): chunk for chunk in chunks}
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                results.append(data)
                print(f"Processed chunk {data['id']} (Entities: {len(data['entities'])}, Relationships: {len(data['relationships'])})")
            except Exception as e:
                pass
                
    print("\nWriting to Graph Database...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    total_entities = 0
    total_rels = 0
    with driver.session() as session:
        for res in results:
            chunk_id = res["id"]
            
            # Map Chunk -> Document
            # We skip mapping Document since we don't have the Document node, but we'll link Entity -> Chunk
            for ent in res["entities"]:
                session.run(
                    "MERGE (e:__Entity__ {name: $name}) SET e:`" + ent['type'] + "` "
                    "MERGE (c:Chunk {id: $chunk_id}) "
                    "MERGE (e)-[:MENTIONED_IN]->(c)",
                    name=ent["name"], chunk_id=chunk_id
                )
                total_entities += 1
                
            for rel in res["relationships"]:
                period = rel["properties"].get("period", "unknown")
                session.run(
                    "MATCH (src {name: $source}) "
                    "MATCH (tgt {name: $target}) "
                    "MERGE (src)-[r:`" + rel["type"] + "` {period: $period}]->(tgt) "
                    "SET r += $props",
                    source=rel["source"], target=rel["target"], period=period, props=rel["properties"]
                )
                total_rels += 1
                
    driver.close()
    
    print(f"Ingested {total_entities} entities and {total_rels} relationships from real data.")
    
    print("\n--- SANITY CHECKS ---")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        for label in ["Company", "Segment", "Metric"]:
            cnt = session.run(f"MATCH (n:{label}) RETURN count(n) as c").single()["c"]
            print(f"{label}s: {cnt}")
            
    print("\n--- SPOT CHECK MENTIONED_IN ---")
    with driver.session() as session:
        res = session.run("MATCH (e)-[:MENTIONED_IN]->(c:Chunk) RETURN e.name as entity, c.text as text LIMIT 3")
        for r in res:
            print(f"Entity: {r['entity']}\nChunk starts with: {r['text'][:100]}...\n")
    driver.close()

if __name__ == "__main__":
    main()
