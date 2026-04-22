import os
import sys
import pytest
import uvicorn
import multiprocessing
import time
import requests
from playwright.sync_api import Page, expect

# Anchoring
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_server():
    from bin.launch_kanban import app
    # Use a different DB for testing to avoid collisions
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test_kanban.db"
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

@pytest.fixture(scope="module", autouse=True)
def server():
    p = multiprocessing.Process(target=run_server)
    p.start()
    # Wait for server to start
    for _ in range(10):
        try:
            requests.get("http://127.0.0.1:8001")
            break
        except:
            time.sleep(0.5)
    yield
    p.terminate()
    if os.path.exists("test_kanban.db"):
        os.remove("test_kanban.db")

def test_kanban_workflow(page: Page):
    page.goto("http://127.0.0.1:8001")
    
    # Check Board Title
    expect(page.locator("#board-name")).to_have_text("Board 1")
    
    # Check Initial Columns
    expect(page.locator(".column-header").nth(0)).to_have_text("To Do")
    expect(page.locator(".column-header").nth(1)).to_have_text("Doing")
    expect(page.locator(".column-header").nth(2)).to_have_text("Done")
    
    # Create a Task
    page.click("text=+ Add Task")
    page.fill("#task-title", "Test Playwright")
    page.fill("#task-desc", "Automation test")
    page.fill("#task-tags", "test,e2e")
    page.click("#create-task-btn")
    # Verify Task appears
    expect(page.locator(".task-card")).to_have_text("Test Playwright")
    
    # Open Task Details
    page.click(".task-card")
    expect(page.locator("#det-title")).to_have_text("Test Playwright")
    expect(page.locator("#det-desc")).to_have_text("Automation test")
    page.click("text=Close")
    
    # Test Drag and Drop (Simulated via API/Event since native DnD in Playwright can be tricky)
    # But let's try native
    source = page.locator(".task-card")
    target = page.locator(".task-list").nth(1) # 'Doing' column
    source.drag_to(target)
    
    # Verify persistence after reload
    page.reload()
    expect(page.locator(".task-list").nth(1).locator(".task-card")).to_have_text("Test Playwright")
