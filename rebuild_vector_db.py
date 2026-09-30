import os
import pymupdf4llm
from dotenv import load_dotenv
from langchain_text_splitters import MarkdownTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jVector
from langchain_core.documents import Document
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
import hashlib
from core.db import get_structured_synthesis_chat
from neo4j import GraphDatabase

load_dotenv()

AURA_INSTANCENAME = os.environ["AURA_INSTANCENAME"]
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

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

async def extract_chunk_graph(chunk_id: str, text: str, semaphore: asyncio.Semaphore, llm):
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
            # We use ainvoke for asynchronous execution
            result = await llm.ainvoke(prompt)
            if hasattr(result, 'entities'):
                return result.entities, result.relationships
        except Exception as e:
            print(f"Failed extraction for chunk {chunk_id}: {e}")
        return [], []

async def main():
    print("1. Parsing PDF to Markdown (preserving tables)...")
    md_text = pymupdf4llm.to_markdown(r"Annual Report\NASDAQ_AAPL_2024.pdf")
    
    print("2. Splitting Markdown into chunks...")
    splitter = MarkdownTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks = splitter.split_text(md_text)
    
    documents = []
    doc_ids = []
    for chunk in chunks:
        chunk_id = "chunk_" + hashlib.md5(chunk.encode('utf-8')).hexdigest()
        doc_ids.append(chunk_id)
        documents.append(Document(page_content=chunk, metadata={"id": chunk_id}))
    
    print(f"Created {len(documents)} markdown documents.")
    
    print("3. Initializing Embedding Model...")
    hf = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': False}
    )
    
    print("4. Pushing new Markdown Vectors to Neo4j...")
    vector_index = Neo4jVector.from_documents(
        documents,
        hf,
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        index_name="vector_markdown",
        keyword_index_name="keyword_markdown",
        search_type="hybrid",
        database=NEO4J_USERNAME,
        ids=doc_ids,
        pre_delete_collection=False
    )
    print("Vector insertion complete.")
    
    print("5. Skipping Async Graph Extraction (Disabled for Vector Restore)...")
    
    print("Done! The database now has properly formatted Markdown tables and an integrated Knowledge Graph.")

if __name__ == "__main__":
    asyncio.run(main())
