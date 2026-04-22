import sys
import os
import pytest
import asyncio
from playwright.async_api import async_playwright
import uvicorn
from multiprocessing import Process
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bin.launch_kanban import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

@pytest.fixture(scope="module")
def server():
    if os.path.exists("./kanban.db"):
        os.remove("./kanban.db")
    
    proc = Process(target=run_server, daemon=True)
    proc.start()
    time.sleep(3) # Wait for startup
    yield
    proc.terminate()
    proc.join()
    if os.path.exists("./kanban.db"):
        os.remove("./kanban.db")

@pytest.mark.asyncio
async def test_kanban_e2e(server):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("http://127.0.0.1:8000/")
        
        # Verify initial columns
        columns = await page.locator(".column").all()
        assert len(columns) == 3
        
        # Add Task via Modal
        # Wait for the board to load
        await page.wait_for_selector(".add-task-btn")
        await page.locator(".add-task-btn").first.click()
        await page.wait_for_selector("#addTaskModal", state="visible")
        
        await page.fill("#newTaskTitle", "Test Task")
        await page.fill("#newTaskDesc", "Description")
        await page.fill("#newTaskTags", "test,playwright")
        await page.click("#create-task-btn")
        
        # Wait for modal to hide
        await page.wait_for_selector("#addTaskModal", state="hidden")
        
        # Verify task is created
        task_locator = page.locator(".task")
        await task_locator.wait_for()
        assert await task_locator.count() == 1
        
        text = await task_locator.text_content()
        assert "Test Task" in text
        
        # View Task via Modal
        await task_locator.click()
        await page.wait_for_selector("#viewTaskModal", state="visible")
        title = await page.locator("#viewTaskTitle").text_content()
        assert title == "Test Task"
        desc = await page.locator("#viewTaskDesc").text_content()
        assert desc == "Description"
        await page.click("text='Close'")
        await page.wait_for_selector("#viewTaskModal", state="hidden")
        
        # Drag and Drop
        # Playwright drag_to simulates mousedown, mousemove, mouseup
        # If it doesn't trigger HTML5 drag/drop correctly, we might need manual event dispatch, 
        # but modern Playwright drag_to handles HTML5.
        target_col = columns[1].locator(".task-list")
        await task_locator.drag_to(target_col)
        
        # Wait a moment for network fetch
        await asyncio.sleep(1)
        
        # Check task moved
        tasks_in_c2 = await columns[1].locator(".task").count()
        assert tasks_in_c2 == 1
        
        await browser.close()