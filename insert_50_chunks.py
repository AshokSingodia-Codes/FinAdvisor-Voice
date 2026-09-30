import os
import pymupdf4llm
from langchain_text_splitters import MarkdownTextSplitter
from langchain_core.documents import Document
from neo4j import GraphDatabase
import hashlib
from dotenv import load_dotenv

load_dotenv()

print("Parsing PDF to Markdown (preserving tables)...")
md_text = pymupdf4llm.to_markdown(r"Annual Report\NASDAQ_AAPL_2024.pdf")

print("Splitting Markdown into chunks...")
splitter = MarkdownTextSplitter(chunk_size=1200, chunk_overlap=200)
chunks = splitter.split_text(md_text)

print(f"Created {len(chunks)} markdown documents.")

# Select first 50
chunks_50 = chunks[:50]

print("Writing 50 chunks to Neo4j...")
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

with driver.session() as session:
    for chunk in chunks_50:
        chunk_id = "chunk_" + hashlib.md5(chunk.encode('utf-8')).hexdigest()
        session.run("MERGE (c:Chunk {id: $id}) SET c.text = $text", id=chunk_id, text=chunk)
        
driver.close()
print("Done inserting 50 chunks.")
