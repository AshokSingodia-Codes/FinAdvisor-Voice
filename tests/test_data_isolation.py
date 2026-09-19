import pytest
import time
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
