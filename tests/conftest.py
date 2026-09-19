import sys
from unittest.mock import MagicMock

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# We mock langchain_neo4j and langchain_huggingface globally before any test modules are imported.
# This prevents core.db from attempting to connect to a live Neo4j database 
# or download HuggingFace models during pytest collection.
mock_langchain_neo4j = MagicMock()
sys.modules['langchain_neo4j'] = mock_langchain_neo4j
sys.modules['langchain_neo4j.graphs.neo4j_graph'] = mock_langchain_neo4j

mock_hf = MagicMock()
sys.modules['langchain_huggingface'] = mock_hf
sys.modules['langchain_huggingface.embeddings'] = mock_hf
sys.modules['langchain_huggingface.embeddings.huggingface'] = mock_hf
