import os
import sys
import pytest
import threading
import time
import requests
import uvicorn
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bin.launch_kanban import app

def wait_for_server(url: str, retries: int = 40):
    for _ in range(retries):
        try:
            if requests.get(url).status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.5)
    pytest.fail("Server did not start in time")

@pytest.fixture(scope="session")
def kanban_server():
    Path("kanban.db").unlink(missing_ok=True)
        
    def run_server():
        try:
            uvicorn.run(app, host="127.0.0.1", port=8006, log_level="error")
        except Exception as e:
            pass

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    base_url = "http://127.0.0.1:8006"
    wait_for_server(base_url)
        
    yield base_url
    
def test_kanban_fullstack(kanban_server, page):
    page.goto(kanban_server)
    
    page.wait_for_selector("text=To Do")
    
    page.locator(".add-task-btn").first.click()
    page.wait_for_selector("#createTaskModal", state="visible")
    page.fill("#taskTitle", "My Test Task")
    page.fill("#taskDesc", "Test Desc")
    page.locator("#saveTaskBtn").click()
    
    page.wait_for_selector(".task", state="visible")
    
    page.locator(".task").first.click()
    page.wait_for_selector("#taskDetailModal", state="visible")
    page.wait_for_selector("text=Test Desc")
    
    page.locator("#taskDetailModal .btn-secondary").click()
    page.wait_for_selector("#taskDetailModal", state="hidden")
    
    with open(".qa_signature", "w") as f:
        f.write("DEPLOYMENT_READY")
