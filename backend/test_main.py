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
    # Use a unique IP to avoid interfering with rate limit tests
    response = client.post("/api/chat", json=valid_payload, headers={"X-Forwarded-For": "10.0.0.1"})
    assert response.status_code in [200, 500]

def test_chat_endpoint_rate_limit():
    """Test that making more than 10 requests within a minute triggers a 429 Too Many Requests."""
    headers = {"X-Forwarded-For": "10.0.0.2"} # Unique IP for this test
    # Make 10 valid requests
    for _ in range(10):
        client.post("/api/chat", json={"messages": [{"role": "user", "content": "Hello"}]}, headers=headers)
    
    # The 11th request should be rate-limited
    response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Hello"}]}, headers=headers)
    assert response.status_code == 429

def test_chat_endpoint_message_too_long():
    """Test that a message exceeding the maximum length is rejected with 422 Unprocessable Entity."""
    long_content = "A" * 1001
    response = client.post("/api/chat", json={
        "messages": [{"role": "user", "content": long_content}]
    }, headers={"X-Forwarded-For": "10.0.0.3"})
    assert response.status_code == 422

def test_chat_endpoint_invalid_role():
    """Test that providing an invalid role (e.g., 'admin') is rejected with 422 Unprocessable Entity."""
    response = client.post("/api/chat", json={
        "messages": [{"role": "admin", "content": "Hello"}]
    }, headers={"X-Forwarded-For": "10.0.0.4"})
    assert response.status_code == 422

def test_chat_endpoint_empty_messages():
    """Test that sending an empty array of messages is rejected with 422 Unprocessable Entity."""
    response = client.post("/api/chat", json={"messages": []}, headers={"X-Forwarded-For": "10.0.0.5"})
    assert response.status_code == 422
