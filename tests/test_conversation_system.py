import pytest
import uuid
import time
from fastapi.testclient import TestClient
from main import app
from core.auth import hash_password, create_access_token
from core.memory import (
    create_user,
    create_conversation,
    get_conversations,
    get_conversation,
    rename_conversation,
    delete_conversation,
    get_memory_facts,
    get_conversation_context
)

client = TestClient(app)

@pytest.fixture
def auth_headers():
    test_email = f"conv_user_{int(time.time()*1000)}@test.com"
    user = create_user(test_email, hash_password("Password123!"))
    token = create_access_token({"sub": test_email, "user_id": user["id"]})
    return {"Authorization": f"Bearer {token}"}

def test_conversation_crud_endpoints(auth_headers):
    # 1. Create conversation
    res = client.post("/api/conversations", json={"title": "Test Budgeting"}, headers=auth_headers)
    assert res.status_code == 200
    conv_id = res.json()["id"]
    assert res.json()["title"] == "Test Budgeting"
    
    # 2. List conversations
    res = client.get("/api/conversations", headers=auth_headers)
    assert res.status_code == 200
    conv_list = res.json()
    assert any(c["id"] == conv_id for c in conv_list)
    
    # 3. Rename conversation
    res = client.patch(f"/api/conversations/{conv_id}", json={"title": "Updated Budgeting Title"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Updated Budgeting Title"
    
    # 4. Retrieve single conversation
    res = client.get(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Updated Budgeting Title"
    assert "messages" in res.json()
    
    # 5. Delete conversation
    res = client.delete(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "deleted"
    
    # Verify deletion
    res = client.get(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert res.status_code == 404

def test_multi_turn_financial_memory_and_isolation(auth_headers):
    """
    Validates the exact multi-turn memory flow and conversation isolation:
    Chat A: Income 20,000, Expenses 12,000, Savings 1 lakh -> Ask investment -> asks & remembers info.
    Chat B: Asks 'What is my monthly income?' -> Must NOT know ₹20,000.
    Back to Chat A: Asks income & expenses -> Returns 20,000 and 12,000.
    """
    conv_id_a = str(uuid.uuid4())
    
    # Step 1: Age, student, income
    r1 = client.post("/api/chat", json={
        "message": "I am a 21-year-old Indian student and I earn ₹20,000 per month.",
        "conversation_id": conv_id_a
    }, headers=auth_headers)
    assert r1.status_code == 200
    
    # Check that facts are extracted
    facts_a = get_memory_facts(conv_id_a)
    assert "20,000" in str(facts_a) or "20000" in str(facts_a)
    assert "21" in str(facts_a)
    
    # Step 2: Expenses
    r2 = client.post("/api/chat", json={
        "message": "My monthly expenses are ₹12,000.",
        "conversation_id": conv_id_a
    }, headers=auth_headers)
    assert r2.status_code == 200
    facts_a = get_memory_facts(conv_id_a)
    assert "12,000" in str(facts_a) or "12000" in str(facts_a)
    
    # Step 3: Savings
    r3 = client.post("/api/chat", json={
        "message": "I have ₹1 lakh in savings.",
        "conversation_id": conv_id_a
    }, headers=auth_headers)
    assert r3.status_code == 200
    
    # Step 4: Ask how much to invest
    r4 = client.post("/api/chat", json={
        "message": "How much could I consider investing every month?",
        "conversation_id": conv_id_a
    }, headers=auth_headers)
    assert r4.status_code == 200
    ans4 = r4.json()["answer"]
    # The answer should consider the surplus (20k - 12k = 8k) or savings
    assert any(term in ans4 for term in ["8,000", "8000", "surplus", "budget", "invest", "emergency", "₹"])
    
    # Step 5: Check database persistence (simulating page reload)
    conv_data = client.get(f"/api/conversations/{conv_id_a}", headers=auth_headers).json()
    assert len(conv_data["messages"]) == 8 # 4 user + 4 assistant
    
    # Step 6: Separate Chat B (Isolation test)
    conv_id_b = str(uuid.uuid4())
    r_b = client.post("/api/chat", json={
        "message": "What is my monthly income?",
        "conversation_id": conv_id_b
    }, headers=auth_headers)
    assert r_b.status_code == 200
    ans_b = r_b.json()["answer"]
    # Chat B must NOT know the income of 20,000 from Chat A
    assert "20,000" not in ans_b and "20000" not in ans_b
    
    # Step 7: Return to Chat A and ask for income
    r7 = client.post("/api/chat", json={
        "message": "What was my monthly income?",
        "conversation_id": conv_id_a
    }, headers=auth_headers)
    assert r7.status_code == 200
    ans7 = r7.json()["answer"]
    assert "20,000" in ans7 or "20000" in ans7
    
    # Step 8: Return to Chat A and ask for expenses
    r8 = client.post("/api/chat", json={
        "message": "What were my monthly expenses?",
        "conversation_id": conv_id_a
    }, headers=auth_headers)
    assert r8.status_code == 200
    ans8 = r8.json()["answer"]
    assert "12,000" in ans8 or "12000" in ans8
    
    # Step 9: Continue financial plan
    r9 = client.post("/api/chat", json={
        "message": "Based on everything we discussed, continue my financial plan.",
        "conversation_id": conv_id_a
    }, headers=auth_headers)
    assert r9.status_code == 200
    ans9 = r9.json()["answer"]
    assert len(ans9) > 50
