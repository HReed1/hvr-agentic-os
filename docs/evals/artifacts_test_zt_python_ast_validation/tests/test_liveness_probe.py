import sys
sys.path.insert(0, ".staging")

from fastapi.testclient import TestClient
from api.main import app, liveness_probe

client = TestClient(app)

def test_liveness_probe_route():
    response = client.get("/live")
    assert response.status_code == 200
    # Assuming it should return some successful JSON, but 200 is a good start.
    # The Executor stub doesn't have a route, so it will return 404.

def test_liveness_probe_exists():
    assert callable(liveness_probe)
