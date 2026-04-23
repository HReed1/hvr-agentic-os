import pytest
import asyncio
import subprocess
import time
import requests
import os
import sys
from playwright.async_api import async_playwright

# AST Namespace Confinement
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(scope="session")
def server():
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bin", "launch_kanban.py"))
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    proc = subprocess.Popen([sys.executable, script_path], env=env)
    
    url = "http://127.0.0.1:8000/"
    timeout = 15
    start = time.time()
    ready = False
    
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                ready = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
            
    if not ready:
        proc.terminate()
        pytest.fail("Server did not bind in time.")
        
    yield
    proc.terminate()

@pytest.mark.asyncio
async def test_kanban_e2e(server):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("http://127.0.0.1:8000/")
        
        # Validate DOM and State Load
        await page.wait_for_selector("text=Board 1")
        await page.wait_for_selector("text=To Do")
        await page.wait_for_selector("text=Doing")
        await page.wait_for_selector("text=Done")
        
        # Native modal interactions
        await page.click("text='+' >> nth=0")
        await page.wait_for_selector("#task-modal", state="visible")
        await page.fill("#task-title", "Omega Task")
        await page.fill("#task-desc", "Critical system test")
        await page.fill("#task-tags", "E2E")
        await page.click("#task-modal button:has-text('Create Task')")
        
        # Wait for recursive state to persist and re-render
        await page.wait_for_selector(".task:has-text('Omega Task')")
        
        # Drag and Drop
        await page.drag_and_drop(".task:has-text('Omega Task')", ".column:has-text('Doing')")
        await page.wait_for_timeout(1000)
        
        # Assert structure natively mapped node states
        doing_col = page.locator(".column:has-text('Doing')")
        assert await doing_col.locator(".task:has-text('Omega Task')").count() == 1
        
        # Detail Modal
        await page.click(".task:has-text('Omega Task')")
        await page.wait_for_selector("#detail-modal", state="visible")
        await page.wait_for_selector("#detail-title:has-text('Omega Task')")
        await page.wait_for_selector("#detail-desc:has-text('Critical system test')")
        await page.click("#detail-modal button:has-text('Close')")
        
        await browser.close()
