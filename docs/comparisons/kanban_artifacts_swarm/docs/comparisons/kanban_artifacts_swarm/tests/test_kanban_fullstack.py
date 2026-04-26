import os
import subprocess
import time
import requests
import pytest
from playwright.sync_api import Page, expect

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "kanban.db")

@pytest.fixture(scope="session", autouse=True)
def boot_server():
    # Teardown any existing DB before test
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    server = subprocess.Popen(
        ["uvicorn", "bin.launch_kanban:app", "--port", "8005", "--host", "127.0.0.1"],
        env=env
    )
    
    # Synchronous readiness polling loop
    max_retries = 30
    ready = False
    for i in range(max_retries):
        try:
            r = requests.get("http://127.0.0.1:8005/")
            if r.status_code in (200, 404):
                ready = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
            
    if not ready:
        server.kill()
        raise RuntimeError("Uvicorn failed to bind within the polling window (ERR_CONNECTION_REFUSED)")
        
    yield
    server.kill()
    server.wait()
    
    # Teardown test DB
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

def test_kanban_board_render(page: Page):
    page.goto("http://127.0.0.1:8005/")
    
    # Check default seeded columns
    expect(page.locator("text='To Do'")).to_be_visible()
    expect(page.locator("text='Doing'")).to_be_visible()
    expect(page.locator("text='Done'")).to_be_visible()

def test_kanban_task_creation_and_modal(page: Page):
    page.goto("http://127.0.0.1:8005/")
    
    # Open new task modal
    page.click("#btn-new-task")
    expect(page.locator("#task-modal")).to_be_visible()
    
    # Fill in task details
    page.fill("#task-title-input", "Playwright Task")
    page.fill("#task-desc-input", "Testing E2E Kanban")
    page.fill("#task-tags-input", "e2e, testing")
    page.click("#btn-save-task")
    
    # Validate task appears in 'To Do' column
    todo_col = page.locator(".kanban-column").filter(has_text="To Do")
    expect(todo_col.locator("text='Playwright Task'")).to_be_visible()

def test_kanban_drag_and_drop(page: Page):
    page.goto("http://127.0.0.1:8005/")
    
    task = page.locator(".kanban-task", has_text="Playwright Task")
    doing_col = page.locator(".kanban-column", has_text="Doing")
    
    # Native Drag and Drop
    task.drag_to(doing_col)
    
    # Validate it moved
    expect(doing_col.locator("text='Playwright Task'")).to_be_visible()

def test_kanban_task_details_modal(page: Page):
    page.goto("http://127.0.0.1:8005/")
    
    task = page.locator(".kanban-task", has_text="Playwright Task")
    task.click()
    
    expect(page.locator("#task-detail-modal")).to_be_visible()
    expect(page.locator("#detail-title", has_text="Playwright Task")).to_be_visible()
    expect(page.locator("#detail-desc", has_text="Testing E2E Kanban")).to_be_visible()
    expect(page.locator("#detail-tags", has_text="e2e, testing")).to_be_visible()
