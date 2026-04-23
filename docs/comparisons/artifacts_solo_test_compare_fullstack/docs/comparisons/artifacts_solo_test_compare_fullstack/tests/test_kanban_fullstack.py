import pytest
import subprocess
import time
import requests
import os
import sys
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def server():
    # Remove existing db to ensure clean state
    db_path = "kanban.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    proc = subprocess.Popen([sys.executable, "bin/launch_kanban.py"])
    
    # Polling for readiness
    ready = False
    for _ in range(30):
        try:
            res = requests.get("http://localhost:8000/")
            if res.status_code == 200:
                ready = True
                break
        except Exception:
            pass
        time.sleep(1)
        
    if not ready:
        proc.kill()
        raise RuntimeError("Server failed to start")
        
    yield "http://localhost:8000"
    
    proc.kill()
    proc.wait()

def test_kanban_e2e(server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Browser error: {err}"))
        page.goto(server)
        # Check board title
        assert page.title() == "Kanban Board"
        page.wait_for_function("document.getElementById('board-name').innerText === 'Board 1'")
        # Wait for columns
        page.wait_for_selector(".column")
        columns = page.query_selector_all(".column")
        assert len(columns) == 3
        
        # Add a task to first column
        # Using specific class or title
        page.click(".add-task-btn")
        page.wait_for_selector("#task-modal.active", state="visible")
        
        page.fill("#task-title", "Test Task")
        page.fill("#task-desc", "This is a test description.")
        page.fill("#task-tags", "test, e2e")
        page.click("#save-task-btn")
        
        # Wait for modal to close and task to appear
        page.wait_for_selector("#task-modal.active", state="hidden")
        page.wait_for_selector(".task")
        
        tasks = page.query_selector_all(".task")
        assert len(tasks) == 1
        
        task_title_el = page.query_selector(".task .task-title")
        assert task_title_el.inner_text() == "Test Task"
        
        # Open details modal
        tasks[0].click()
        page.wait_for_selector("#detail-modal.active", state="visible")
        assert page.inner_text("#detail-title") == "Test Task"
        assert "This is a test description." in page.inner_text("#detail-desc")
        
        # Check tags rendered
        tags = page.query_selector_all("#detail-tags .tag")
        assert len(tags) == 2
        assert tags[0].inner_text() == "test"
        assert tags[1].inner_text() == "e2e"
        
        page.click("#detail-modal .btn") # close
        page.wait_for_selector("#detail-modal.active", state="hidden")
        
        # Add a column
        page.click("text=+ Add Column")
        page.wait_for_selector("#col-modal.active", state="visible")
        page.fill("#col-name", "Review")
        page.click("#col-modal .btn:has-text('Create Column')")
        page.wait_for_selector("#col-modal.active", state="hidden")
        
        # Wait for 4 columns
        page.wait_for_function("document.querySelectorAll('.column').length === 4")
        
        # Clean shutdown check
        browser.close()
