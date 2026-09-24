import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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

import pytest
import time
from core.auth import hash_password, create_access_token
from core.memory import create_user

@pytest.fixture
def auth_headers():
    test_email = f"test_user_{int(time.time()*1000)}@test.com"
    user = create_user(test_email, hash_password("Password123!"))
    token = create_access_token({"sub": test_email, "user_id": user["id"]})
    return {"Authorization": f"Bearer {token}"}
