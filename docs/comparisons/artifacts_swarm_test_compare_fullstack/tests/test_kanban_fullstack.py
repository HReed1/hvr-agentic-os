import pytest
import multiprocessing
import time
import requests
import os
import sys
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_server():
    import uvicorn
    from bin.launch_kanban import app
    uvicorn.run(app, host="127.0.0.1", port=8000)

def wait_for_server():
    max_retries = 20
    for i in range(max_retries):
        try:
            r = requests.get("http://127.0.0.1:8000/")
            if r.status_code in [200, 404]:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False

@pytest.fixture(scope="session", autouse=True)
def boot_server():
    db_path = os.path.join(os.path.dirname(__file__), "..", "kanban.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    server = multiprocessing.Process(target=run_server)
    server.start()
    
    if not wait_for_server():
        server.terminate()
        server.join()
        raise RuntimeError("Uvicorn failed to bind within the polling window (ERR_CONNECTION_REFUSED)")
        
    yield
    server.terminate()
    server.join()
    
    if os.path.exists(db_path):
        os.remove(db_path)

def test_kanban_board():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Test Root HTML load
        response = page.goto("http://127.0.0.1:8000/")
        assert response.status == 200, "Failed to load kanban root page"
        
        # Test seeded columns
        assert page.locator("text=To Do").is_visible(), "To Do column missing"
        assert page.locator("text=Doing").is_visible(), "Doing column missing"
        assert page.locator("text=Done").is_visible(), "Done column missing"
        
        # Open Create Task modal
        page.click("button:has-text('Add Task')")
        
        # Fill custom modal form (NO browser prompts)
        page.fill("input[name='title']", "Test Task")
        page.fill("textarea[name='description']", "Test description")
        page.fill("input[name='tags']", "test")
        page.click("button:has-text('Save')")
        
        # Verify task is rendered in column
        assert page.locator("text=Test Task").is_visible()
        
        browser.close()
