from fastapi.testclient import TestClient
from main import app
import uuid
import pytest

client = TestClient(app)

def test_indian_stock_query():
    conv_id = str(uuid.uuid4())
    response = client.post("/api/chat", json={
        "message": "What is the current price of Reliance?",
        "conversation_id": conv_id,
        "chat_history": []
    })
    
    assert response.status_code == 200
    answer = response.json()["answer"]
    
    # We check if it attempted to resolve the stock or fallback safely
    assert "RELIANCE.NS" in answer or "Live market data isn't currently available" in answer

def test_student_advisor_query():
    conv_id = str(uuid.uuid4())
    response = client.post("/api/chat", json={
        "message": "I am an Indian student earning ₹20,000 per month. How should I start managing my money?",
        "conversation_id": conv_id,
        "chat_history": []
    })
    
    assert response.status_code == 200
    answer = response.json()["answer"]
    
    # Check if the model is giving step by step guidance
    assert "budget" in answer.lower() or "emergency" in answer.lower() or "save" in answer.lower()
    # Check that it mentions risk or explicitly states things aren't guaranteed
    assert "risk" in answer.lower() or "not guarantee" in answer.lower() or "disclaimer" in answer.lower() or "assume" in answer.lower() or "not guaranteed" in answer.lower()

def test_company_comparison():
    conv_id = str(uuid.uuid4())
    response = client.post("/api/chat", json={
        "message": "Compare HDFC Bank and ICICI Bank.",
        "conversation_id": conv_id,
        "chat_history": []
    })
    
    assert response.status_code == 200
    answer = response.json()["answer"]
    
    # Should contain a structured comparison (e.g. table format or distinct points) and both banks
    assert "HDFC" in answer and "ICICI" in answer
    assert "|" in answer # Proxy for markdown table or structured separation
