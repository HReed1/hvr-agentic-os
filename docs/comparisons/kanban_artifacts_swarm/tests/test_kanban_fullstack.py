import os
import sys
import time
import pytest
import requests
import subprocess
from playwright.sync_api import Page, expect

# Path injection for local discovery
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(scope="module")
def kanban_server():
    # Setup: Ensure DB is seeded using SEED_ONLY to avoid blocking
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env["SEED_ONLY"] = "1"
    
    # Run seeding
    subprocess.run([sys.executable, "bin/launch_kanban.py"], 
                   env=env, timeout=10, capture_output=True)
    
    # Clear SEED_ONLY and spawn server
    env.pop("SEED_ONLY", None)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "bin.launch_kanban:app", "--host", "127.0.0.1", "--port", "8000"],
        env=env
    )
    
    # Polling readiness loop
    max_retries = 30
    ready = False
    for i in range(max_retries):
        try:
            res = requests.get("http://127.0.0.1:8000/", timeout=1)
            if res.status_code == 200:
                ready = True
                break
        except Exception:
            time.sleep(0.5)
    
    if not ready:
        proc.terminate()
        pytest.fail("Kanban server failed to start")
        
    yield "http://127.0.0.1:8000"
    
    proc.terminate()
    proc.wait()
    if os.path.exists("kanban.db"):
        os.remove("kanban.db")

def test_kanban_flow(kanban_server, page: Page):
    page.goto(kanban_server)
    
    # 1. Verify Columns exist (seeded)
    expect(page.get_by_text("To Do")).to_be_visible()
    expect(page.get_by_text("Doing")).to_be_visible()
    expect(page.get_by_text("Done")).to_be_visible()
    
    # 2. Create a Task
    page.locator(".column h2 button").first.click()
    expect(page.get_by_text("New Task")).to_be_visible()
    
    page.fill("#taskTitle", "Refactor Logic")
    page.fill("#taskDesc", "Simplify the AST traversals")
    page.fill("#taskTags", "backend, complexity")
    page.click("#modalAction")
    
    # Verify task appears
    expect(page.locator(".task-card")).to_contain_text("Refactor Logic")
    
    # 3. View Task Detail
    page.click("text=Refactor Logic")
    expect(page.get_by_text("Task Details")).to_be_visible()
    expect(page.get_by_text("Simplify the AST traversals")).to_be_visible()
    expect(page.get_by_text("backend")).to_be_visible()
    page.click("text=Close")
    
    # 4. Drag and Drop
    task = page.locator(".task-card")
    doing_col = page.locator(".task-list").nth(1)
    
    task.drag_to(doing_col)
    
    # Verify it moved
    expect(doing_col.locator(".task-card")).to_contain_text("Refactor Logic")
