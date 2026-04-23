import os
import sys
import time
import subprocess
import pytest
import requests
from playwright.sync_api import sync_playwright

def wait_for_server():
    for _ in range(30):
        try:
            if requests.get("http://localhost:8000/").status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    pytest.fail("Server did not start in time.")

@pytest.fixture(scope="module")
def kanban_server():
    db_path = os.path.join(os.path.dirname(__file__), "..", "kanban.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    launcher_path = os.path.join(os.path.dirname(__file__), "..", "bin", "launch_kanban.py")
    process = subprocess.Popen([sys.executable, launcher_path])
    
    wait_for_server()
        
    yield "http://localhost:8000"
    
    process.terminate()
    process.wait()

def test_kanban_fullstack(kanban_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(kanban_server)
        
        page.wait_for_selector("#board-title")
        assert page.locator("#board-title").inner_text() == "Board 1"
        
        page.click("#add-column-btn")
        page.wait_for_selector("#columnModal", state="visible")
        page.fill("[data-testid='col-name-input']", "Testing Column")
        page.click("#save-col-btn")
        
        page.wait_for_selector("text=Testing Column")
        
        page.wait_for_selector(".add-task-btn")
        add_task_btns = page.locator(".add-task-btn")
        add_task_btns.nth(0).click()
        
        page.wait_for_selector("#taskModal", state="visible")
        page.fill("[data-testid='task-title-input']", "My First Task")
        page.fill("[data-testid='task-desc-input']", "Task Description")
        page.fill("[data-testid='task-tags-input']", "test")
        page.click("#save-task-btn")
        
        page.wait_for_selector("text=My First Task")
        
        page.click("text=My First Task")
        page.wait_for_selector("#viewTaskModal", state="visible")
        assert page.locator("[data-testid='view-task-title']").inner_text() == "My First Task"
        assert page.locator("[data-testid='view-task-desc']").inner_text() == "Task Description"
        assert page.locator("[data-testid='view-task-tags']").inner_text() == "test"
        page.click("#close-view-task-btn")
        
        browser.close()
