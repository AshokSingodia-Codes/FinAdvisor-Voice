import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv

# Ensure project root in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_text_splitters import MarkdownTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jVector
from langchain_core.documents import Document

load_dotenv()

NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

if not NEO4J_URI:
    print("Error: NEO4J_URI not configured.")
    sys.exit(1)

guide_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "personal_finance_and_tax_guide.md")

if not os.path.exists(guide_path):
    print(f"Error: Guide file not found at {guide_path}")
    sys.exit(1)

print("\n=======================================================")
print("📚 Ingesting Indian Tax & Personal Wealth Corpus into Neo4j")
print("=======================================================\n")

# 1. Read Markdown
with open(guide_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

# 2. Semantic Markdown Splitter
# Using chunk_size=1000 with 150 overlap to preserve table structures and tax rules intact
splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=150)
chunks = splitter.split_text(raw_text)

documents = [
    Document(
        page_content=chunk,
        metadata={
            "source": "Indian_Tax_and_Personal_Wealth_Guide_2024_25",
            "category": "tax_and_personal_finance",
            "chunk_id": f"tax_wealth_{i:03d}"
        }
    )
    for i, chunk in enumerate(chunks, 1)
]

print(f"Generated {len(documents)} high-density semantic chunks.")

# 3. Initialize 768-dim Embedding Model
print("Initializing Sentence-Transformers all-mpnet-base-v2 (768 dims)...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': False}
)

# 4. Connect to Neo4j Vector & Fulltext Indexes
print("Connecting to Neo4j Aura 'vector_markdown' and 'keyword_markdown'...")
vector_index = Neo4jVector.from_existing_index(
    embeddings,
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name="vector_markdown",
    keyword_index_name="keyword_markdown",
    search_type="hybrid",
    database=NEO4J_USERNAME
)

# 5. Ingest into Neo4j
print("Ingesting chunks into Neo4j...")
vector_index.add_documents(documents)

print(f"\n🎉 Successfully ingested {len(documents)} chunks of Personal Finance & Indian Tax Knowledge into Neo4j Aura!")
