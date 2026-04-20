import os
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)
from core.auth import verify_token
app.dependency_overrides[verify_token] = lambda: {"sub": "test_user"}

response = client.get("/samples/SMPL-VIRAL-REAL")
print("API RESPONSE CODE:", response.status_code)
import json
print("API BODY RUN METADATA:", json.dumps(response.json()["runs"][0]["metadata_col"], indent=2))
