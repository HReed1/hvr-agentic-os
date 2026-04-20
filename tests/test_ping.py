import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_ping_endpoint():
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pong"
    assert "timestamp" in data
