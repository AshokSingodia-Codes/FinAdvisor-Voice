import pytest
import time
import io
from fastapi.testclient import TestClient
from main import app
from core.auth import hash_password, create_access_token
from core.memory import create_user, get_conversations, get_conversation

client = TestClient(app)

def test_complete_multi_user_data_isolation():
    # Setup User A
    user_a_email = f"user_a_{int(time.time())}@isolation.com"
    user_a_pwd = "PasswordA123!"
    user_a = create_user(user_a_email, hash_password(user_a_pwd))
    token_a = create_access_token({"sub": user_a_email, "user_id": user_a["id"]})
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Setup User B
    user_b_email = f"user_b_{int(time.time())}@isolation.com"
    user_b_pwd = "PasswordB123!"
    user_b = create_user(user_b_email, hash_password(user_b_pwd))
    token_b = create_access_token({"sub": user_b_email, "user_id": user_b["id"]})
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # =========================================================================
    # Test 1 — User A: Create conversation & send message
    # =========================================================================
    conv_a_res = client.post("/api/conversations", json={"title": "User A Private Portfolio"}, headers=headers_a)
    assert conv_a_res.status_code == 200
    conv_a_id = conv_a_res.json()["id"]

    chat_a_res = client.post("/api/chat", json={
        "message": "User A secret financial plan: invest 10 lakh in mutual funds",
        "conversation_id": conv_a_id
    }, headers=headers_a)
    assert chat_a_res.status_code == 200

    # Verify User A sees their conversation
    list_a = client.get("/api/conversations", headers=headers_a).json()
    assert len(list_a) == 1
    assert list_a[0]["id"] == conv_a_id
    assert list_a[0]["title"] == "User A Private Portfolio"

    # =========================================================================
    # Test 2 — User B: Verify User A's conversation does NOT appear
    # =========================================================================
    list_b = client.get("/api/conversations", headers=headers_b).json()
    assert len(list_b) == 0, "User B should NOT see User A's conversation in the list"
    assert not any(c["id"] == conv_a_id for c in list_b)

    # User B creates their own conversation
    conv_b_res = client.post("/api/conversations", json={"title": "User B Budgeting"}, headers=headers_b)
    assert conv_b_res.status_code == 200
    conv_b_id = conv_b_res.json()["id"]

    chat_b_res = client.post("/api/chat", json={
        "message": "User B query: what is emergency fund?",
        "conversation_id": conv_b_id
    }, headers=headers_b)
    assert chat_b_res.status_code == 200

    # User B list should only contain User B's conversation
    list_b_after = client.get("/api/conversations", headers=headers_b).json()
    assert len(list_b_after) == 1
    assert list_b_after[0]["id"] == conv_b_id
    assert not any(c["id"] == conv_a_id for c in list_b_after)

    # =========================================================================
    # Test 3 — Switch back to User A: Verify only User A's conversations appear
    # =========================================================================
    list_a_check = client.get("/api/conversations", headers=headers_a).json()
    assert len(list_a_check) == 1
    assert list_a_check[0]["id"] == conv_a_id
    assert not any(c["id"] == conv_b_id for c in list_a_check)

    # User A retrieves their conversation and sees their messages
    conv_a_detail = client.get(f"/api/conversations/{conv_a_id}", headers=headers_a)
    assert conv_a_detail.status_code == 200
    messages_a = conv_a_detail.json()["messages"]
    assert len(messages_a) >= 2
    assert "User A secret financial plan" in messages_a[0]["content"]

    # =========================================================================
    # Test 4 — Unauthorized Direct Access: User B requests User A's conversation ID
    # =========================================================================
    unauth_get = client.get(f"/api/conversations/{conv_a_id}", headers=headers_b)
    assert unauth_get.status_code in [403, 404], "User B must be rejected when accessing User A conversation"
    assert "User A secret financial plan" not in unauth_get.text

    # =========================================================================
    # Test 5 — API-Level Security: User B tries to modify/delete/chat in User A's conversation
    # =========================================================================
    # 5a. Rename attempt
    unauth_rename = client.patch(
        f"/api/conversations/{conv_a_id}",
        json={"title": "Hacked Title"},
        headers=headers_b
    )
    assert unauth_rename.status_code == 403

    # 5b. Delete attempt
    unauth_delete = client.delete(f"/api/conversations/{conv_a_id}", headers=headers_b)
    assert unauth_delete.status_code == 403

    # 5c. Chat hijacking attempt (posting message to User A's conversation)
    unauth_chat = client.post("/api/chat", json={
        "message": "User B intruder message",
        "conversation_id": conv_a_id
    }, headers=headers_b)
    assert unauth_chat.status_code == 403

    # Verify User A's conversation is still intact and unchanged
    conv_a_verify = client.get(f"/api/conversations/{conv_a_id}", headers=headers_a).json()
    assert conv_a_verify["title"] == "User A Private Portfolio"
    assert not any("intruder" in m["content"] for m in conv_a_verify["messages"])


# =============================================================================
# Personal Document Isolation Tests
#
# These tests verify the three-field isolation contract:
#   user_id + document_id + conversation_id
#
# Every retrieval query against PersonalChunk nodes MUST be filtered by all
# three fields.  Violations are caught at the API layer before the query
# even reaches Neo4j.
# =============================================================================

def _make_dummy_text_file(content: str = "Test financial document. Salary: 50000. Expenses: 30000.") -> bytes:
    """Returns a UTF-8 encoded plain-text file as bytes."""
    return content.encode("utf-8")


def test_personal_document_isolation():
    """
    Full personal document isolation suite covering:
      - Cross-user document access (User B cannot use User A's document)
      - Cross-conversation isolation: User A, Conversation 2 (same user,
        different conversation_id, no re-attach) MUST NOT surface
        Conversation 1's document chunks.
      - Unauthorized deletion attempt

    Sub-tests:
      A — User B references User A's doc_id → 403
      B — User A references doc from Conversation 1 while in Conversation 2 → 403
      C — User A in Conversation 2 with NO document_id (no re-attach) →
              shared corpus response must NOT contain private document data
      D — User B attempts to delete User A's document → 403
      E — User A deletes their own document → 200
      F — After deletion, referencing the document returns 404
    """
    ts = int(time.time())

    # --- Setup User A ---
    user_a_email = f"doc_user_a_{ts}@isolation.com"
    user_a = create_user(user_a_email, hash_password("DocPassA123!"))
    token_a = create_access_token({"sub": user_a_email, "user_id": user_a["id"]})
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # --- Setup User B ---
    user_b_email = f"doc_user_b_{ts}@isolation.com"
    user_b = create_user(user_b_email, hash_password("DocPassB123!"))
    token_b = create_access_token({"sub": user_b_email, "user_id": user_b["id"]})
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # =========================================================================
    # Setup: User A — Conversation 1, upload a document
    # =========================================================================
    conv1_res = client.post("/api/conversations", json={"title": "A Doc Conv 1"}, headers=headers_a)
    assert conv1_res.status_code == 200
    conv1_id = conv1_res.json()["id"]

    doc_content = _make_dummy_text_file(
        "MONTHLY STATEMENT\nSalary: \u20b985,000\nRent: \u20b918,000\nFood: \u20b912,000\n"
        "Savings: \u20b915,000\nULIP premium: \u20b95,000\nNet balance: \u20b935,000"
    )
    upload_res = client.post(
        "/api/documents/upload",
        data={"conversation_id": conv1_id},
        files={"file": ("statement.txt", io.BytesIO(doc_content), "text/plain")},
        headers=headers_a,
    )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    doc_id = upload_res.json()["document_id"]
    assert doc_id, "document_id must be returned on successful upload"

    # =========================================================================
    # Test A: User B CANNOT use User A's document — 403 on chat with doc
    # =========================================================================
    conv_b_res = client.post("/api/conversations", json={"title": "B Conv"}, headers=headers_b)
    assert conv_b_res.status_code == 200
    conv_b_id = conv_b_res.json()["id"]

    cross_user_chat = client.post("/api/chat", json={
        "message": "What is my salary?",
        "conversation_id": conv_b_id,
        "document_id": doc_id,  # User A's document — must be rejected
    }, headers=headers_b)
    assert cross_user_chat.status_code == 403, (
        f"User B should receive 403 when referencing User A's document. "
        f"Got {cross_user_chat.status_code}: {cross_user_chat.text}"
    )

    # =========================================================================
    # Test B: User A CANNOT use the document in a different conversation — 403
    #
    # Same user, but document was uploaded to conv1_id.
    # Attempting to reference it from conv2_id (no re-attach) must be rejected.
    # =========================================================================
    conv2_res = client.post("/api/conversations", json={"title": "A Doc Conv 2"}, headers=headers_a)
    assert conv2_res.status_code == 200
    conv2_id = conv2_res.json()["id"]

    cross_conv_chat = client.post("/api/chat", json={
        "message": "What is my monthly salary from my statement?",
        "conversation_id": conv2_id,   # ← different conversation than upload
        "document_id": doc_id,          # ← document was uploaded to conv1_id
    }, headers=headers_a)
    assert cross_conv_chat.status_code == 403, (
        f"User A in Conversation 2 should receive 403 when using a document from Conversation 1 "
        f"without re-attaching. Got {cross_conv_chat.status_code}: {cross_conv_chat.text}"
    )
    assert "different conversation" in cross_conv_chat.json().get("detail", "").lower(), (
        "Error detail should mention the conversation mismatch."
    )

    # =========================================================================
    # Test C (per approval decision #4):
    # User A starts Conversation 2, asks the same question WITHOUT document_id
    # (no re-attach). The retriever must fall through to the shared corpus path.
    # The private document data (₹85,000 salary) must NOT appear in the answer.
    # =========================================================================
    shared_corpus_chat = client.post("/api/chat", json={
        "message": "What is my monthly salary from my uploaded statement?",
        "conversation_id": conv2_id,
        # document_id deliberately omitted — simulating new conversation, no re-attach
    }, headers=headers_a)
    assert shared_corpus_chat.status_code == 200, (
        f"Chat in Conversation 2 without document should succeed (shared corpus). "
        f"Got {shared_corpus_chat.status_code}: {shared_corpus_chat.text}"
    )
    answer_text = shared_corpus_chat.json().get("answer", "")
    # The shared corpus has no knowledge of this personal upload.
    # If 85000 or the ₹85,000 figure appears, the isolation has been breached.
    assert "85,000" not in answer_text and "85000" not in answer_text, (
        "Conversation 2 (no document attached) must NOT surface chunks from "
        "the document uploaded in Conversation 1. The shared corpus path must "
        "be used exclusively when document_id is absent."
    )

    # =========================================================================
    # Test D: User B CANNOT delete User A's document — 403
    # =========================================================================
    unauth_delete = client.delete(
        f"/api/documents/{doc_id}",
        params={"conversation_id": conv1_id},
        headers=headers_b,
    )
    assert unauth_delete.status_code == 403, (
        f"User B must receive 403 when attempting to delete User A's document. "
        f"Got {unauth_delete.status_code}: {unauth_delete.text}"
    )

    # =========================================================================
    # Test E: User A CAN delete their own document — 200
    # =========================================================================
    auth_delete = client.delete(
        f"/api/documents/{doc_id}",
        params={"conversation_id": conv1_id},
        headers=headers_a,
    )
    assert auth_delete.status_code == 200, (
        f"User A should be able to delete their own document. "
        f"Got {auth_delete.status_code}: {auth_delete.text}"
    )
    assert auth_delete.json()["status"] == "deleted"

    # =========================================================================
    # Test F: After deletion, referencing the document returns 404
    # =========================================================================
    post_delete_chat = client.post("/api/chat", json={
        "message": "What was my salary?",
        "conversation_id": conv1_id,
        "document_id": doc_id,
    }, headers=headers_a)
    assert post_delete_chat.status_code == 404, (
        f"After deletion, referencing the document must return 404. "
        f"Got {post_delete_chat.status_code}: {post_delete_chat.text}"
    )
