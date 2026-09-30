import os
import re
from dotenv import load_dotenv
from langchain_text_splitters import MarkdownTextSplitter
from langchain_core.documents import Document
from pydantic import BaseModel, Field
from typing import List, Optional
import hashlib
import concurrent.futures
from langchain_groq import ChatGroq
from neo4j import GraphDatabase
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jVector
import json
import requests
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
llm_raw = ChatGroq(model_name=MODEL_STRING, temperature=0)
llm = llm_raw.with_structured_output(ExtractionResult)

@retry(stop=stop_after_attempt(50), wait=wait_exponential(multiplier=1, min=10, max=60))
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

def check_groq_model(model_name: str):
    print(f"Validating model '{model_name}' against live endpoint...")
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not set.")
    headers = {"Authorization": f"Bearer {groq_api_key}"}
    response = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10)
    response.raise_for_status()
    models = response.json().get("data", [])
    model_names = [m["id"] for m in models]
    if model_name not in model_names:
        raise ValueError(f"\n🚨 [STARTUP FAILED] Model '{model_name}' not found! Available models:\n{model_names}\n")
    print(f"Model '{model_name}' verified successfully.")

def main():
    check_groq_model(MODEL_STRING)
    print("1. Reading Cached Markdown...")
    with open('cached_10k.md', 'r', encoding='utf-8') as f:
        md_text = f.read()

    print("2. Extracting exact text spans using regex for section headers...")
    
    match_1a_start = re.search(r'###### \*\*Item 1A\..*?Risk Factors\*\*', md_text, re.IGNORECASE)
    match_1b_start = re.search(r'###### \*\*Item 1B\..*?Unresolved', md_text, re.IGNORECASE)
    match_7_start = re.search(r'###### \*\*Item 7\..*?Management', md_text, re.IGNORECASE)
    match_7a_start = re.search(r'###### \*\*Item 7A\..*?Quantitative', md_text, re.IGNORECASE)

    subset_text = ""
    
    if match_1a_start and match_1b_start:
        item_1a_text = md_text[match_1a_start.end():match_1b_start.start()]
        subset_text += item_1a_text + "\n\n"
        print(f"Extracted Item 1A: {len(item_1a_text)} characters")
    else:
        print("Failed to match Item 1A bounds!")
        
    if match_7_start and match_7a_start:
        item_7_text = md_text[match_7_start.end():match_7a_start.start()]
        subset_text += item_7_text + "\n\n"
        print(f"Extracted Item 7: {len(item_7_text)} characters")
    else:
        print("Failed to match Item 7 bounds!")

    if not subset_text:
        print("Fallback to first 100k chars.")
        subset_text = md_text[:100000]

    print("3. Splitting Text into Chunks...")
    splitter = MarkdownTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks = splitter.split_text(subset_text)
    chunks = chunks[:105]
    
    print(f"Created {len(chunks)} Markdown chunks.")

    documents = []
    doc_ids = []
    for chunk in chunks:
        chunk_id = "chunk_sub_" + hashlib.md5(chunk.encode('utf-8')).hexdigest()
        doc_ids.append(chunk_id)
        documents.append(Document(page_content=chunk, metadata={"id": chunk_id}))
        
    print("4. Clearing existing Vector and Graph Data (if starting fresh)...")
    checkpoint_file = "processed_chunks.json"
    processed_chunks = set()
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            try:
                processed_chunks = set(json.load(f))
            except json.JSONDecodeError:
                pass

    if not processed_chunks:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as session:
            session.run("MATCH (e:__Entity__) DETACH DELETE e")
            session.run("MATCH (c:Chunk) DETACH DELETE c")
        driver.close()
        print("Graph cleared.")
    else:
        print(f"Resuming from checkpoint ({len(processed_chunks)} chunks). Skipping graph wipe.")

    print("5. Pushing Markdown Vectors to Neo4j (if starting fresh)...")
    if not processed_chunks:
        # Bypassing LangChain Neo4jVector to avoid Aura index hangs
        print("Bypassing LangChain vector index creation. Uploading Chunks via Cypher...")
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as session:
            for chunk_id, chunk_text in zip(doc_ids, chunks):
                cypher = "MERGE (c:Chunk {id: $id}) SET c.text = $text"
                session.run(cypher, id=chunk_id, text=chunk_text)
        driver.close()
        print("Chunks uploaded successfully.")
    else:
        print("Skipping vector push since we are resuming.")

    print("6. Starting Sync Graph Extraction (Concurrency=2)...")
    checkpoint_file = "processed_chunks.json"
    processed_chunks = set()
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            try:
                processed_chunks = set(json.load(f))
            except json.JSONDecodeError:
                pass
    
    print(f"Loaded {len(processed_chunks)} previously processed chunks from checkpoint.")
    
    results = []
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    total_entities = 0
    total_rels = 0
    
    def process_and_save_chunk(chunk_id, chunk_text):
        if chunk_id in processed_chunks:
            return None
            
        ents, rels = extract_chunk_graph(chunk_id, chunk_text)
        
        # Write to Neo4j immediately
        with driver.session() as session:
            for ent in ents:
                cypher = f"MERGE (n:__Entity__ {{name: $name}}) SET n:`{ent.type}`"
                session.run(cypher, name=ent.name)
                
                cypher_mention = """
                MATCH (e:__Entity__ {name: $name})
                MATCH (c:Chunk {id: $chunk_id})
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
                    
        # Update checkpoint file after successful DB write
        processed_chunks.add(chunk_id)
        with open(checkpoint_file, 'w') as f:
            json.dump(list(processed_chunks), f)
            
        return (len(ents), len(rels))

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(process_and_save_chunk, doc_ids[i], chunks[i]): i for i in range(len(chunks))}
        for future in concurrent.futures.as_completed(futures):
            i = futures[future]
            try:
                res = future.result()
                if res is not None:
                    ents_cnt, rels_cnt = res
                    total_entities += ents_cnt
                    total_rels += rels_cnt
                    print(f"Processed chunk {i+1}/{len(chunks)}")
                else:
                    print(f"Skipped chunk {i+1}/{len(chunks)} (already processed)")
            except Exception as e:
                print(f"Chunk {i+1} failed completely.")
    
    print(f"Ingested {total_entities} entities and {total_rels} relationships from subset in this run.")
    
    print("7. Writing Graph Entities & Relationships to Neo4j with Time-Series MERGE and __Entity__ label...")
    total_entities = 0
    # Removed old bulk write block since we write incrementally now

    print("\n--- SANITY CHECKS ---")
    with driver.session() as session:
        for label in ["Company", "Segment", "Metric"]:
            cnt = session.run(f"MATCH (n:{label}) RETURN count(n) as c").single()["c"]
            print(f"{label}s: {cnt}")
            
    print("\n--- SPOT CHECK MENTIONED_IN ---")
    with driver.session() as session:
        res = session.run("MATCH (e)-[:MENTIONED_IN]->(c:Chunk) RETURN e.name as entity, substring(c.text, 0, 150) as text LIMIT 5")
        for r in res:
            print(f"Entity: {r['entity']}")
            print(f"Chunk starts with: {repr(r['text'])}...\n")
            
    print("\n--- CHECK FOR STALE 'The Company' NODES ---")
    with driver.session() as session:
        res = session.run("MATCH (c:Company) RETURN c.name as name")
        for r in res:
            print(f"Company Node: {r['name']}")
            
    driver.close()
    
    print("Done! Real Subset extraction complete.")

if __name__ == "__main__":
    main()
