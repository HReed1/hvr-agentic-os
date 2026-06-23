# mock_codebase/tests/test_routes.py
import pytest
from fastapi.testclient import TestClient
from mock_codebase.app.routes import app

client = TestClient(app)

def test_get_tasks_no_params():
    # Test default fetching (limit=10, offset=0, no filter)
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, dict)
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert data["total"] == 5
    assert len(data["items"]) == 5

def test_get_tasks_filtering():
    # Test filtering by status
    response = client.get("/api/tasks?status=completed")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 2
    assert all(item["status"] == "completed" for item in data["items"])

def test_get_tasks_pagination():
    # Test limit and offset pagination
    response = client.get("/api/tasks?limit=2&offset=1")
    assert response.status_code == 200
    data = response.json()
    
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert len(data["items"]) == 2
    # Check that it returns items at index 1 and 2
    assert data["items"][0]["id"] == "2"
    assert data["items"][1]["id"] == "3"

def test_get_tasks_validation_errors():
    # Test limit boundary validation (< 1)
    response_low = client.get("/api/tasks?limit=0")
    assert response_low.status_code == 422
    
    # Test limit boundary validation (> 100)
    response_high = client.get("/api/tasks?limit=101")
    assert response_high.status_code == 422
    
    # Test negative offset validation
    response_neg = client.get("/api/tasks?offset=-5")
    assert response_neg.status_code == 422
