import os
import pymupdf4llm
from dotenv import load_dotenv
from langchain_text_splitters import MarkdownTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jVector
from langchain_core.documents import Document
from pydantic import BaseModel, Field
from typing import List, Optional
import hashlib
import concurrent.futures
from langchain_groq import ChatGroq
from neo4j import GraphDatabase
import re
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

AURA_INSTANCENAME = os.environ["AURA_INSTANCENAME"]
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

# Define schema models
class ExtractedEntity(BaseModel):
    name: str = Field(description="The canonical name of the entity.")
    type: str = Field(description="The type (Company, Segment, RiskFactor, Concept, Metric).")
    
class ExtractedRelationship(BaseModel):
    source_entity: str = Field(description="Exact name of the source entity.")
    target_entity: str = Field(description="Exact name of the target entity.")
    relationship: str = Field(description="Relationship (HAS_SEGMENT, FACES_RISK, REPORTED_METRIC, DRIVES_METRIC, DEPENDS_ON).")
    properties: dict = Field(description="Optional properties for the edge, e.g., value, period, unit for metrics.", default_factory=dict)

class ExtractionResult(BaseModel):
    entities: List[ExtractedEntity]
    relationships: List[ExtractedRelationship]

MODEL_STRING = "openai/gpt-oss-120b"
llm_raw = ChatGroq(model_name=MODEL_STRING, temperature=0, max_tokens=4000, api_key=os.environ["GROQ_API_KEY"])
llm = llm_raw.with_structured_output(ExtractionResult)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
def extract_chunk_graph(chunk_id: str, text: str):
    prompt = f"""
    You are an expert financial knowledge extractor. 
    Extract entities and relationships from the following text based on this strict schema.
    
    Allowed Entity Types: Company, Segment, RiskFactor, Concept, Metric
    Allowed Relationships: HAS_SEGMENT, FACES_RISK, REPORTED_METRIC, DRIVES_METRIC, DEPENDS_ON
    
    CRITICAL INSTRUCTIONS:
    1. Only extract entities that fit exactly into the Allowed Entity Types. Discard locations, people, arbitrary nouns.
    2. For metrics, include properties on the REPORTED_METRIC or DRIVES_METRIC edge to capture the value, period, and unit.
    3. CANONICALIZATION RULE FOR METRICS: Extract base metric names ONLY (e.g., "revenue"). DO NOT include the segment or company name in the metric name. Map "net sales" to "revenue". Lowercase all metric names.
    4. CANONICALIZATION RULE FOR COMPANIES: Always output "Apple Inc." if Apple or "the Company" is mentioned and there is exactly one company in context.
    5. CANONICALIZATION RULE FOR SEGMENTS: Always output "iPhone" if the iPhone segment is mentioned.
    
    Text:
    [CHUNK_ID: {chunk_id}]
    {text}
    """
    try:
        result = llm.invoke(prompt)
        if hasattr(result, 'entities'):
            return result.entities, result.relationships
    except Exception as e:
        print(f"Failed extraction for chunk {chunk_id}: {e}")
        raise e
    return [], []

def main():
    print("1. Parsing PDF to Markdown (preserving tables)...")
    md_text = pymupdf4llm.to_markdown(r"Annual Report\NASDAQ_AAPL_2024.pdf")
    
    print("2. Extracting Subset (Item 1A and Item 7)...")
    
    idx_1a = md_text.lower().find("item 1a.")
    idx_1b = md_text.lower().find("item 1b.", idx_1a) if idx_1a != -1 else -1
    
    idx_7 = md_text.lower().find("item 7.")
    idx_7a = md_text.lower().find("item 7a.", idx_7) if idx_7 != -1 else -1
    
    subset_text = ""
    if idx_1a != -1 and idx_1b != -1:
        subset_text += md_text[idx_1a:idx_1b] + "\n\n"
    if idx_7 != -1 and idx_7a != -1:
        subset_text += md_text[idx_7:idx_7a] + "\n\n"
        
    if not subset_text:
        print("Find failed to match sections. Using first 50000 chars as fallback.")
        subset_text = md_text[:50000]
        
    print("3. Splitting Subset Markdown into chunks...")
    splitter = MarkdownTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks = splitter.split_text(subset_text)
    
    # chunks = chunks[:20]  # Removed chunk limit for full subset

    
    documents = []
    doc_ids = []
    for chunk in chunks:
        chunk_id = "chunk_" + hashlib.md5(chunk.encode('utf-8')).hexdigest()
        doc_ids.append(chunk_id)
        documents.append(Document(page_content=chunk, metadata={"id": chunk_id}))
    
    print(f"Created {len(documents)} markdown documents.")
    
    print("4. Pushing new Markdown Vectors to Neo4j...")
    hf = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': False}
    )
    vector_index = Neo4jVector.from_documents(
        documents,
        hf,
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        index_name="vector_markdown",
        search_type="hybrid",
        database=NEO4J_USERNAME,
        ids=doc_ids
    )
    print("Vector insertion complete.")
    
    print("5. Starting Sync Graph Extraction (Concurrency=5)...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(extract_chunk_graph, doc_ids[i], chunks[i]): i for i in range(len(chunks))}
        for future in concurrent.futures.as_completed(futures):
            i = futures[future]
            try:
                ents, rels = future.result()
                results.append((doc_ids[i], ents, rels))
                print(f"Processed chunk {i+1}/{len(chunks)}")
            except Exception as e:
                print(f"Chunk {i+1} failed completely.")
    
    print("6. Writing Graph Entities & Relationships to Neo4j with Time-Series MERGE and __Entity__ label...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    total_entities = 0
    total_rels = 0
    
    with driver.session() as session:
        for (chunk_id, ents, rels) in results:
            for ent in ents:
                # Enforce __Entity__ label alongside specific type
                cypher = f"MERGE (n:__Entity__ {{name: $name}}) SET n:`{ent.type}`"
                session.run(cypher, name=ent.name)
                total_entities += 1
                
                # Link to chunk using MENTIONED_IN
                cypher_mention = """
                MATCH (e:__Entity__ {name: $name})
                MERGE (c:Chunk {id: $chunk_id})
                MERGE (e)-[:MENTIONED_IN]->(c)
                """
                session.run(cypher_mention, name=ent.name, chunk_id=chunk_id)
                
            for rel in rels:
                props = rel.properties or {}
                period = props.get('period')
                
                if period:
                    cypher = f"""
                    MATCH (src:__Entity__ {{name: $source}})
                    MATCH (tgt:__Entity__ {{name: $target}})
                    MERGE (src)-[r:`{rel.relationship}` {{period: $period}}]->(tgt)
                    SET r += $props
                    """
                    session.run(cypher, source=rel.source_entity, target=rel.target_entity, period=period, props=props)
                else:
                    cypher = f"""
                    MATCH (src:__Entity__ {{name: $source}})
                    MATCH (tgt:__Entity__ {{name: $target}})
                    MERGE (src)-[r:`{rel.relationship}`]->(tgt)
                    SET r += $props
                    """
                    session.run(cypher, source=rel.source_entity, target=rel.target_entity, props=props)
                total_rels += 1
    driver.close()
    
    print(f"Ingested {total_entities} entities and {total_rels} relationships from subset.")

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
            print(f"Entity: {r['entity']}")
            print(f"Chunk starts with: {r['text'][:100]}...\n")
    driver.close()
    
    print("Done! Subset extraction complete.")

if __name__ == "__main__":
    main()
