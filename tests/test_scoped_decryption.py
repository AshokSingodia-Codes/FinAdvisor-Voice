import io
import time
import pytest
from fastapi.testclient import TestClient
from core.auth import hash_password, create_access_token
from core.memory import create_user
from core.document_store import MAX_FILE_BYTES
from core.memory import create_user as create_memory_user
from core.crypto import encrypt_text
from retrieval.personal_retriever import get_all_personal_document_chunks
from main import app

client = TestClient(app)

@pytest.fixture
def user_and_token():
    test_email = f"test_user_{int(time.time()*1000)}@test.com"
    user = create_user(test_email, hash_password("Password123!"))
    token = create_access_token({"sub": test_email, "user_id": user["id"]})
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers

def test_scoped_decryption_chunk_count(user_and_token):
    user, headers = user_and_token
    # Create a conversation
    conv_res = client.post("/api/conversations", json={"title": "Test Conv"}, headers=headers)
    assert conv_res.status_code == 200
    conv_id = conv_res.json()["id"]

    # Generate dummy text with many lines to produce multiple chunks
    dummy_text = "\n".join([f"Line {i}: Sample financial content with amount ₹{i*1000}" for i in range(1, 101)])
    content_bytes = dummy_text.encode()
    assert len(content_bytes) > 5000  # ensure non-trivial size

    # Mock the embeddings so zip(chunks, embeddings) doesn't yield empty
    from unittest.mock import patch
    
    with patch('core.db.hf.embed_documents', side_effect=lambda texts: [[0.1]*768 for _ in texts]):
        # Upload document
        upload_res = client.post(
            "/api/documents/upload",
            data={"conversation_id": conv_id},
            files={"file": ("statement.txt", io.BytesIO(content_bytes), "text/plain")},
            headers=headers,
        )
        assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
        doc_id = upload_res.json()["document_id"]

    # Poll status
    for _ in range(10):
        status_res = client.get(f"/api/documents/status/{doc_id}", headers=headers)
        assert status_res.status_code == 200
        if status_res.json()["status"] == "ready":
            break
        time.sleep(0.5)
    else:
        pytest.fail("Document ingestion timed out.")

    # Verify chunk count matches limit and decryption returns plaintext strings
    from unittest.mock import patch
    import core.crypto

    # Since Neo4j is mocked globally in conftest, extract inserted chunks from the mock
    from core.db import kg
    inserted_chunks = []
    print(f"\nDEBUG CALL_ARGS_LIST: {kg.query.call_args_list}")
    for call in kg.query.call_args_list:
        if call.args and "UNWIND $batch AS item" in call.args[0]:
            inserted_chunks.extend(call.args[1]["batch"])
            
    def fake_query(cypher, params=None):
        if "RETURN c.text AS text" in cypher:
            return [{"text": item["text"]} for item in inserted_chunks[:params.get("limit", limit)]]
        return []
        
    kg.query.side_effect = fake_query

    limit = 20
    with patch('retrieval.personal_retriever.decrypt_text', wraps=core.crypto.decrypt_text) as mock_decrypt:
        chunks = get_all_personal_document_chunks(
            user_id=user["id"],
            document_id=doc_id,
            conversation_id=conv_id,
            limit=limit,
        )
        assert isinstance(chunks, list)
        assert len(chunks) > 0, f"Expected > 0 chunks, got {len(chunks)}"
        # Assert exactly k calls happened
        assert mock_decrypt.call_count == len(chunks), f"Expected {len(chunks)} decrypt calls, got {mock_decrypt.call_count}"
        for chunk in chunks:
            assert isinstance(chunk, str) and len(chunk) > 0
