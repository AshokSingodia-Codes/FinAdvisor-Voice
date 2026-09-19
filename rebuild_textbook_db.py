import os
from dotenv import load_dotenv
from langchain_text_splitters import MarkdownTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jVector
from langchain_core.documents import Document

load_dotenv()

AURA_INSTANCENAME = os.environ.get("AURA_INSTANCENAME")
NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

if not NEO4J_URI:
    print("Error: NEO4J_URI not set in environment.")
    exit(1)

textbook_path = os.path.join("Annual Report", "Ultimate_Finance_Knowledge_Base.md")

if not os.path.exists(textbook_path):
    print(f"Error: {textbook_path} not found. Please run scripts/generate_textbook.py first.")
    exit(1)

print("1. Reading Textbook Markdown...")
with open(textbook_path, "r", encoding="utf-8") as f:
    md_text = f.read()

print("2. Splitting Markdown into chunks...")
splitter = MarkdownTextSplitter(chunk_size=1200, chunk_overlap=200)
chunks = splitter.split_text(md_text)

# Convert string chunks to Document objects with metadata
documents = [
    Document(
        page_content=chunk, 
        metadata={"source": "textbook", "title": "Ultimate Finance & CA Knowledge Base"}
    ) 
    for chunk in chunks
]
print(f"Created {len(documents)} markdown documents.")

print("3. Initializing Embedding Model...")
hf = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': False}
)

print("4. Connecting to existing Neo4j Index and adding new Textbook Vectors...")
# We connect to the existing index so we do NOT overwrite the Apple 10-K past data.
vector_index = Neo4jVector.from_existing_index(
    hf,
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name="vector_markdown",
    keyword_index_name="keyword_markdown",
    search_type="hybrid",
    database=NEO4J_USERNAME
)

# Add the new textbook chunks to the existing database
vector_index.add_documents(documents)

print("Done! The database now contains BOTH the past data (10-K) and the new Ultimate Finance Knowledge Base.")
