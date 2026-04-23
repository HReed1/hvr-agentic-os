import os
import sys
import time
import subprocess
import requests
import pytest
from playwright.sync_api import Page, expect

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(scope="session", autouse=True)
def background_server():
    db_path = os.path.join(os.path.dirname(__file__), "..", "kanban.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    script_path = os.path.join(os.path.dirname(__file__), "..", "bin", "launch_kanban.py")
    proc = subprocess.Popen([sys.executable, script_path])
    
    ready = False
    start_time = time.time()
    while time.time() - start_time < 15:
        try:
            res = requests.get("http://127.0.0.1:8000/")
            if res.status_code == 200:
                ready = True
                break
        except requests.ConnectionError:
            pass
        time.sleep(0.5)
        
    if not ready:
        proc.terminate()
        pytest.fail("Background Uvicorn server failed to bind in time.")
        
    yield
    proc.terminate()
    proc.wait()

def test_kanban_fullstack_flow(page: Page):
    page.goto("http://127.0.0.1:8000/", timeout=15000)
    
    expect(page.locator("h1#boardTitle")).to_contain_text("Board 1")
    
    columns = page.locator(".column-header span")
    expect(columns).to_have_count(3)
    expect(columns.nth(0)).to_have_text("To Do")
    
    add_task_btns = page.locator(".column-header button")
    add_task_btns.nth(0).click()
    
    page.wait_for_selector("#taskModal.active")
    page.fill("#taskTitle", "Test Playwright Task")
    page.fill("#taskDesc", "This is an E2E test task")
    page.fill("#taskTags", "e2e, testing")
    
    page.click("#taskModal button:has-text('Create')")
    page.wait_for_selector("#taskModal.active", state="hidden")
    
    task_locator = page.locator(".task-title", has_text="Test Playwright Task")
    expect(task_locator).to_be_visible()
    
    task_locator.click()
    page.wait_for_selector("#taskDetailModal.active")
    expect(page.locator("#dtlTitle")).to_have_text("Test Playwright Task")
    expect(page.locator("#dtlDesc")).to_have_text("This is an E2E test task")
    expect(page.locator("#dtlTags")).to_have_text("e2e, testing")
    
    page.click("#taskDetailModal button:has-text('Close')")
    page.wait_for_selector("#taskDetailModal.active", state="hidden")
    
    page.click("button:has-text('+ Add Column')")
    page.wait_for_selector("#colModal.active")
    page.fill("#colName", "QA Validation")
    page.click("#colModal button:has-text('Create')")
    page.wait_for_selector("#colModal.active", state="hidden")
    
    expect(page.locator(".column-header span", has_text="QA Validation")).to_be_visible()
