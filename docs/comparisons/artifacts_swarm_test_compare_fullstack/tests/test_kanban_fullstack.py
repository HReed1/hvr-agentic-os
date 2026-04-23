import sys
import os
import time
import pytest
import subprocess
import requests
from playwright.sync_api import Page, expect

@pytest.fixture(scope="session")
def kanban_server():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bin", "launch_kanban.py"))
    
    port = 8045
    env["KANBAN_PORT"] = str(port)
    process = subprocess.Popen(
        [sys.executable, script_path],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    url = f"http://127.0.0.1:{port}"
    
    ready = False
    for _ in range(30):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                ready = True
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.5)
        
    if not ready:
        process.terminate()
        stdout, stderr = process.communicate()
        raise RuntimeError(f"Server failed to start. stderr: {stderr.decode()}")
        
    yield url
    
    process.terminate()
    process.wait(timeout=5)

def test_kanban_fullstack(page: Page, kanban_server: str):
    page.goto(kanban_server)
    page.wait_for_selector(".column-header")
    
    columns = page.locator(".column-header span").all_text_contents()
    assert "To Do" in columns
    assert "Doing" in columns
    assert "Done" in columns
    
    page.click("text=+ Add Column")
    page.wait_for_selector("#columnModal.active")
    page.fill("#colName", "QA Validation")
    page.click("#columnModal >> text=Save")
    
    page.wait_for_selector("text=QA Validation")
    
    first_col_add_btn = page.locator(".column").first.locator("button")
    first_col_add_btn.click()
    
    page.wait_for_selector("#taskModal.active")
    page.fill("#taskTitle", "End-to-End Test Task")
    page.fill("#taskDesc", "Testing modal interactions natively.")
    page.fill("#taskTags", "test, e2e")
    page.click("#taskModal >> text=Save")
    
    page.wait_for_selector(".task >> text=End-to-End Test Task")
    
    page.click(".task >> text=End-to-End Test Task")
    page.wait_for_selector("#viewTaskModal.active")
    
    expect(page.locator("#viewTaskTitle")).to_have_text("End-to-End Test Task")
    expect(page.locator("#viewTaskDesc")).to_have_text("Testing modal interactions natively.")
    expect(page.locator("#viewTaskTags")).to_have_text("test, e2e")
    
    page.click("#viewTaskModal >> text=Close")
    
    source = page.locator(".task >> text=End-to-End Test Task")
    target = page.locator(".task-list").nth(2)
    
    source.drag_to(target)
    
    time.sleep(1)
    done_column_tasks = target.locator(".task").all_text_contents()
    assert any("End-to-End Test" in t for t in done_column_tasks)