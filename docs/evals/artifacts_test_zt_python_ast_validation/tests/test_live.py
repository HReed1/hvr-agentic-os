from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_liveness_probe():
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"status": "live"}
