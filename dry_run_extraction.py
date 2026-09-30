import os
import asyncio
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pydantic import BaseModel, Field
from typing import List, Optional
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Load environment & settings
load_dotenv()
from config.settings import settings

# Determine verified model string from settings (Phase 1 discipline)
from langchain_groq import ChatGroq
MODEL_STRING = "llama3-70b-8192"
llm_raw = ChatGroq(model_name=MODEL_STRING, temperature=0, max_tokens=4000, api_key=settings.GROQ_API_KEY)

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

llm = llm_raw.with_structured_output(ExtractionResult)

# Rate-limited invoke with exponential backoff
@retry(
    wait=wait_exponential(multiplier=2, min=4, max=120),
    stop=stop_after_attempt(10),
    reraise=True
)
async def safe_ainvoke(prompt: str):
    return await llm.ainvoke(prompt)

async def extract_chunk_graph(chunk_id: str, text: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        prompt = f"""
        You are an expert financial knowledge extractor. 
        Extract entities and relationships from the following text based on this strict schema.
        
        Allowed Entity Types: Company, Segment, RiskFactor, Concept, Metric, Chunk
        Allowed Relationships: HAS_SEGMENT, FACES_RISK, REPORTED_METRIC, DRIVES_METRIC, DEPENDS_ON, MENTIONED_IN
        
        CRITICAL INSTRUCTIONS:
        1. Only extract entities that fit exactly into the Allowed Entity Types. Discard locations, people, arbitrary nouns.
        2. The chunk ID is provided in brackets at the top. You MUST extract a Chunk entity for it, and link EVERY OTHER extracted entity to this Chunk using the MENTIONED_IN relationship.
        3. For metrics, include properties on the REPORTED_METRIC or DRIVES_METRIC edge to capture the value, period, and unit.
        4. CANONICALIZATION RULE FOR METRICS: Extract base metric names ONLY (e.g., "revenue"). DO NOT include the segment or company name in the metric name. Map "net sales" to "revenue". Lowercase all metric names.
        5. CANONICALIZATION RULE FOR COMPANIES: Always output "Apple Inc." if Apple is mentioned.
        6. CANONICALIZATION RULE FOR SEGMENTS: Always output "iPhone" if the iPhone segment is mentioned.
        
        Text:
        [CHUNK_ID: {chunk_id}]
        {text}
        """
        try:
            result = await safe_ainvoke(prompt)
            if hasattr(result, 'entities'):
                return chunk_id, result.entities, result.relationships
        except Exception as e:
            print(f"Failed extraction for chunk {chunk_id}: {e}")
        return chunk_id, [], []


async def main():
    print(f"Starting Dry Run with 50 real chunks using model: {MODEL_STRING}")
    
    NEO4J_URI = os.environ["NEO4J_URI"]
    NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
    NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    # 1. Fetch 50 real chunks
    with driver.session() as session:
        # Fetching chunks that already exist in Neo4j from earlier ingestion
        res = session.run("MATCH (c:Chunk) RETURN c.id as id, c.text as text LIMIT 50")
        chunks = [{"id": r["id"], "text": r["text"]} for r in res]
        
    print(f"Fetched {len(chunks)} chunks from Vector index.")
    if len(chunks) == 0:
        print("No chunks found. Is the vector db initialized?")
        return
        
    # 2. Checkpointing setup
    checkpoint_file = "dry_run_processed.json"
    processed_ids = set()
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            processed_ids = set(json.load(f))
            
    to_process = [c for c in chunks if c["id"] not in processed_ids]
    print(f"Skipping {len(chunks) - len(to_process)} already processed chunks. Processing {len(to_process)}...")
    
    # Close driver during long extraction to avoid defunct connection
    driver.close()
    
    # 3. Concurrent Extraction
    semaphore = asyncio.Semaphore(10)
    tasks = [extract_chunk_graph(c["id"], c["text"], semaphore) for c in to_process]
    
    results = await asyncio.gather(*tasks)
    
    # 4. Ingestion with MERGE
    print("Writing to Graph Database...")
    total_ents = 0
    total_rels = 0
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        for chunk_id, ents, rels in results:
            if not ents:
                continue
                
            total_ents += len(ents)
            total_rels += len(rels)
            
            for ent in ents:
                if ent.type == "Chunk":
                    # Chunk was already created by Vector ingestion, MERGE by id just to be safe
                    cypher = "MERGE (n:Chunk {id: $name})"
                else:
                    cypher = f"MERGE (n:`{ent.type}` {{name: $name}})"
                session.run(cypher, name=ent.name)
                
            for rel in rels:
                props = rel.properties or {}
                period = props.get('period')
                
                src_match = "MATCH (src {id: $source})" if "chunk" in rel.source_entity.lower() else "MATCH (src {name: $source})"
                tgt_match = "MATCH (tgt {id: $target})" if "chunk" in rel.target_entity.lower() else "MATCH (tgt {name: $target})"
                
                if period:
                    cypher = f"""
                    {src_match}
                    {tgt_match}
                    MERGE (src)-[r:`{rel.relationship}` {{period: $period}}]->(tgt)
                    SET r += $props
                    """
                    session.run(cypher, source=rel.source_entity, target=rel.target_entity, period=period, props=props)
                else:
                    cypher = f"""
                    {src_match}
                    {tgt_match}
                    MERGE (src)-[r:`{rel.relationship}`]->(tgt)
                    SET r += $props
                    """
                    session.run(cypher, source=rel.source_entity, target=rel.target_entity, props=props)
            
            # Save checkpoint
            processed_ids.add(chunk_id)
            with open(checkpoint_file, "w") as f:
                json.dump(list(processed_ids), f)
                
    print(f"Ingested {total_ents} entities and {total_rels} relationships from real data.")
    
    # 5. Sanity Checks
    print("\n--- SANITY CHECKS ---")
    with driver.session() as session:
        comp_count = session.run("MATCH (c:Company) RETURN count(c) as cnt").single()["cnt"]
        seg_count = session.run("MATCH (s:Segment) RETURN count(s) as cnt").single()["cnt"]
        met_count = session.run("MATCH (m:Metric) RETURN count(m) as cnt").single()["cnt"]
        print(f"Companies: {comp_count}")
        print(f"Segments: {seg_count}")
        print(f"Metrics: {met_count}")
        
        # Spot check 3 MENTIONED_IN edges
        print("\n--- SPOT CHECK MENTIONED_IN ---")
        edges = session.run("MATCH (n)-[r:MENTIONED_IN]->(c:Chunk) WHERE n:Company OR n:Metric RETURN labels(n)[0] as type, n.name as name, c.id as cid, c.text as text LIMIT 3").data()
        for e in edges:
            print(f"Edge: {e['type']}({e['name']}) -> Chunk({e['cid']})")
            print(f"  Chunk Text: {e['text'][:100]}...")
            
    driver.close()

if __name__ == "__main__":
    asyncio.run(main())
