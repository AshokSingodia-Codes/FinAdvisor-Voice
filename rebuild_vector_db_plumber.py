import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jVector

load_dotenv()

NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

print("1. Parsing PDF with PDFPlumber (better table handling)...")
loader = PDFPlumberLoader(r"Annual Report\NASDAQ_AAPL_2024.pdf")
docs = loader.load()

print("2. Splitting text...")
splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
documents = splitter.split_documents(docs)
print(f"Created {len(documents)} documents.")

print("3. Initializing Embedding Model...")
hf = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': False}
)

print("4. Pushing new Vectors to Neo4j...")
vector_index = Neo4jVector.from_documents(
    documents,
    hf,
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name="vector_markdown",
    keyword_index_name="keyword_markdown",
    search_type="hybrid",
    database=NEO4J_USERNAME
)

print("Done! The database now has properly formatted PDF text.")
