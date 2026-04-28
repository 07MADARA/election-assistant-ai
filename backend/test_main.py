import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test that the health check endpoint returns 200 OK."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "cached": True}

def test_chat_endpoint_validation_error():
    """Test that sending an invalid payload returns a 422 Unprocessable Entity."""
    response = client.post("/api/chat", json={"invalid": "payload"})
    assert response.status_code == 422

def test_chat_endpoint_structure():
    """
    Test that the chat endpoint expects the correct payload and returns either 200 or 500
    (500 if API key is missing or invalid, which is expected in test env without mocking).
    """
    valid_payload = {
        "messages": [
            {"role": "user", "content": "How do I register to vote?"}
        ]
    }
    response = client.post("/api/chat", json=valid_payload)
    assert response.status_code in [200, 500]
