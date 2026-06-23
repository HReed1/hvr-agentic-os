# mock_codebase/app/routes.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TaskItem(BaseModel):
    id: str
    title: str
    status: str

# In-memory mock database
MOCK_DB = [
    {"id": "1", "title": "Setup repository", "status": "completed"},
    {"id": "2", "title": "Design mock codebase", "status": "pending"},
    {"id": "3", "title": "Implement git manager", "status": "pending"},
    {"id": "4", "title": "Add test suites", "status": "completed"},
    {"id": "5", "title": "Run baseline benchmarks", "status": "pending"},
]

@app.get("/api/tasks")
def get_tasks():
    """
    Retrieves a list of tasks.
    
    Baseline version:
    - Returns a raw list of all tasks.
    - Lacks pagination (limit/offset) support.
    - Lacks filtering by status.
    """
    return MOCK_DB
