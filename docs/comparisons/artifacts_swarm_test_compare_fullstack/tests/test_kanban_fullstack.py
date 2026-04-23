import os
import time
import pytest
import requests
import subprocess
from playwright.sync_api import Page, expect

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kanban.db"))

@pytest.fixture(scope="session", autouse=True)
def boot_server():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    launcher_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bin", "launch_kanban.py"))
    
    server = subprocess.Popen(["python", launcher_path])
    
    max_retries = 30
    ready = False
    for i in range(max_retries):
        try:
            r = requests.get("http://localhost:8000/")
            if r.status_code in [200, 404]:
                ready = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.2)
            
    if not ready:
        server.kill()
        raise RuntimeError("Server failed to bind within the polling window (ERR_CONNECTION_REFUSED)")
        
    yield
    
    server.kill()
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except Exception:
            pass

def test_kanban_ui(page: Page):
    page.goto("http://localhost:8000/")
    
    expect(page.locator("text=To Do").first).to_be_visible()
    expect(page.locator("text=Doing").first).to_be_visible()
    expect(page.locator("text=Done").first).to_be_visible()
    
    page.click("text=Add Task")
    
    expect(page.locator(".modal").first).to_be_visible()
    
    page.fill("input[name='title']", "QA Test Task")
    page.fill("textarea[name='description']", "TDAID Description")
    page.fill("input[name='tags']", "test, playwright")
    
    page.click("button.submit-btn")
    
    expect(page.locator("text=QA Test Task").first).to_be_visible()
