import os
import pymupdf4llm
from dotenv import load_dotenv
from langchain_text_splitters import MarkdownTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jVector
from langchain_core.documents import Document

load_dotenv()

AURA_INSTANCENAME = os.environ["AURA_INSTANCENAME"]
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

print("1. Parsing PDF to Markdown (preserving tables)...")
md_text = pymupdf4llm.to_markdown(r"Annual Report\NASDAQ_AAPL_2024.pdf")

print("2. Splitting Markdown into chunks...")
splitter = MarkdownTextSplitter(chunk_size=1200, chunk_overlap=200)
chunks = splitter.split_text(md_text)

# Convert string chunks to Document objects
documents = [Document(page_content=chunk) for chunk in chunks]
print(f"Created {len(documents)} markdown documents.")

print("3. Initializing Embedding Model...")
hf = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': False}
)

print("4. Pushing new Markdown Vectors to Neo4j...")
# We will create a brand new index specifically for the markdown tables
vector_index = Neo4jVector.from_documents(
    documents,
    hf,
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name="vector_markdown",
    search_type="hybrid",
    database=NEO4J_USERNAME
)

print("Done! The database now has properly formatted Markdown tables.")
