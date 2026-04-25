import pytest
import time
import requests
import os
import sys
import multiprocessing
import uvicorn
from playwright.sync_api import sync_playwright, expect

# Add staging directory to path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bin.launch_kanban import app, seed_db

PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kanban.db"))

def run_server():
    seed_db()
    uvicorn.run(app, host="127.0.0.1", port=PORT)

def wait_for_server():
    for _ in range(50):
        try:
            r = requests.get(BASE_URL)
            if r.status_code in [200, 404]:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.2)
    return False

@pytest.fixture(scope="session", autouse=True)
def boot_server():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    proc = multiprocessing.Process(target=run_server, daemon=True)
    proc.start()
    
    if not wait_for_server():
        proc.terminate()
        proc.join()
        raise RuntimeError("Server failed to bind within the polling window (ERR_CONNECTION_REFUSED)")
        
    yield BASE_URL
    
    proc.terminate()
    proc.join()
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

@pytest.fixture(scope="function")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        yield page
        browser.close()

def test_kanban_initial_seed(page):
    page.goto(BASE_URL)
    expect(page.locator("text=Board 1")).to_be_visible()
    
    columns = page.locator(".column-title")
    expect(columns).to_have_count(3)
    expect(columns.nth(0)).to_have_text("To Do")
    expect(columns.nth(1)).to_have_text("Doing")
    expect(columns.nth(2)).to_have_text("Done")

def test_kanban_create_task_modal(page):
    page.goto(BASE_URL)
    page.click("#btn-create-task")
    modal = page.locator("#create-task-modal")
    expect(modal).to_be_visible()
    
    page.fill("#task-title-input", "New UI Task")
    page.fill("#task-desc-input", "Description of the UI task")
    page.fill("#task-tags-input", "frontend, ui")
    page.click("#btn-submit-task")
    
    expect(modal).to_be_hidden()
    task = page.locator(".task-card", has_text="New UI Task")
    expect(task).to_be_visible()

def test_kanban_task_details_modal(page):
    page.goto(BASE_URL)
    
    # Create the task first
    page.click("#btn-create-task")
    page.fill("#task-title-input", "Details Task")
    page.fill("#task-desc-input", "Some detail info")
    page.fill("#task-tags-input", "details")
    page.click("#btn-submit-task")
    
    task = page.locator(".task-card", has_text="Details Task")
    task.click()
    
    details_modal = page.locator("#task-details-modal")
    expect(details_modal).to_be_visible()
    expect(details_modal.locator(".task-detail-title")).to_contain_text("Details Task")
    expect(details_modal.locator(".task-detail-desc")).to_contain_text("Some detail info")
    expect(details_modal.locator(".task-detail-tags")).to_contain_text("details")
    
    page.click("#btn-close-details")
    expect(details_modal).to_be_hidden()

def test_kanban_drag_and_drop(page):
    page.goto(BASE_URL)
    
    page.click("#btn-create-task")
    page.fill("#task-title-input", "Drag Task")
    page.click("#btn-submit-task")
    
    source = page.locator(".task-card", has_text="Drag Task").first
    target = page.locator(".column").nth(1)
    
    source.drag_to(target)
    expect(target.locator(".task-card", has_text="Drag Task")).to_be_visible()
    
    page.reload()
    target_reloaded = page.locator(".column").nth(1)
    expect(target_reloaded.locator(".task-card", has_text="Drag Task")).to_be_visible()
