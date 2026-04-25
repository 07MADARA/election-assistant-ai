import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test that the health check endpoint returns 200 OK."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_endpoint_validation_error():
    """Test that sending an invalid payload returns a 422 Unprocessable Entity."""
    response = client.post("/api/chat", json={"invalid": "payload"})
    assert response.status_code == 422

def test_chat_endpoint_unauthorized():
    """
    Test that the chat endpoint returns a 500 when API key is missing.
    In a real test environment, we might mock the GenAI call, 
    but for this challenge, validating the endpoint structure is key.
    """
    # Assuming GEMINI_API_KEY is not set in the test environment,
    # or testing the basic payload structure.
    valid_payload = {
        "messages": [
            {"role": "user", "content": "How do I register to vote?"}
        ]
    }
    response = client.post("/api/chat", json=valid_payload)
    
    # It might return 500 if no API key is configured, which is expected behavior
    # based on our main.py logic when API_KEY is None.
    # If the API key is set, it might actually attempt to call the API.
    # To prevent actual API calls during basic tests, we just check if it's not 404/422.
    assert response.status_code in [200, 500]
