import pytest
import multiprocessing
import uvicorn
import time
import os
import sys
import re

from playwright.sync_api import Page, expect

# Add parent to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bin.launch_kanban import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

@pytest.fixture(scope="module")
def server():
    if os.path.exists("./kanban.db"):
        os.remove("./kanban.db")
        
    proc = multiprocessing.Process(target=run_server, daemon=True)
    proc.start()
    time.sleep(2) # wait for server to start
    yield
    proc.terminate()
    proc.join()
    
    if os.path.exists("./kanban.db"):
        os.remove("./kanban.db")

def test_kanban_flow(server, page: Page):
    page.goto("http://127.0.0.1:8000/")
    
    # Check board loaded with 3 columns
    expect(page.locator(".column-header").nth(0)).to_contain_text("To Do")
    expect(page.locator(".column-header").nth(1)).to_contain_text("Doing")
    expect(page.locator(".column-header").nth(2)).to_contain_text("Done")

    # Create a new task
    page.locator(".column-header button").nth(0).click()
    expect(page.locator("#taskModal")).to_have_class(re.compile(r"show"))
    
    page.fill("#task-title", "E2E Task")
    page.fill("#task-desc", "This is an E2E test task")
    page.fill("#task-tags", "test, e2e")
    
    page.locator("#taskModal button:has-text('Create')").click()
    
    # Wait for modal to disappear
    expect(page.locator("#taskModal")).not_to_have_class(re.compile(r"show"))
    
    # The task should appear in the first column
    task_locator = page.locator(".task").nth(0)
    expect(task_locator).to_have_text("E2E Task")
    
    # Check detail modal
    task_locator.click()
    expect(page.locator("#detailModal")).to_have_class(re.compile(r"show"))
    expect(page.locator("#task-detail-title")).to_have_text("E2E Task")
    expect(page.locator("#task-detail-description")).to_have_text("This is an E2E test task")
    
    # Close detail modal
    page.locator("#detailModal button:has-text('Close')").click()
    expect(page.locator("#detailModal")).not_to_have_class(re.compile(r"show"))
    
    # Test column creation
    page.locator("text=+ Add Column").click()
    expect(page.locator("#colModal")).to_have_class(re.compile(r"show"))
    
    page.fill("#col-name", "Backlog")
    page.locator("#colModal button:has-text('Create')").click()
    expect(page.locator("#colModal")).not_to_have_class(re.compile(r"show"))
    
    expect(page.locator(".column-header").nth(3)).to_contain_text("Backlog")
    
    # Drag and Drop test
    source = page.locator(".task").nth(0)
    target = page.locator(".column-body").nth(1)
    
    source.drag_to(target)
    
    # Verify it moved
    expect(page.locator(".column-body").nth(1).locator(".task")).to_have_count(1)
    expect(page.locator(".column-body").nth(0).locator(".task")).to_have_count(0)
