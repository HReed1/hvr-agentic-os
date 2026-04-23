import os
import subprocess
import time
import requests
import pytest
import pytest_asyncio
from playwright.async_api import async_playwright

DB_PATH = ".staging/app.db"
DB_PATH_LOCAL = "app.db"

@pytest_asyncio.fixture(scope="session", autouse=True)
def boot_server():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(DB_PATH_LOCAL):
        os.remove(DB_PATH_LOCAL)

    server = subprocess.Popen(["python", "-m", "uvicorn", "api.main:app", "--port", "8000"])
    
    max_retries = 20
    ready = False
    for i in range(max_retries):
        try:
            r = requests.get("http://localhost:8000/live")
            if r.status_code == 200 or r.status_code == 404:
                ready = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.2)
            
    if not ready:
        server.kill()
        raise RuntimeError("Uvicorn failed to bind within the polling window (ERR_CONNECTION_REFUSED)")
        
    yield
    
    server.kill()
    server.wait(timeout=5)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(DB_PATH_LOCAL):
        os.remove(DB_PATH_LOCAL)

@pytest.mark.asyncio
async def test_add_item_strict_mode():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(record_video_dir="videos/")
        page = await context.new_page()
        
        await page.goto("http://localhost:8000/")
        
        await page.fill("input[name='name']", "Test Item")
        await page.click("button:has-text('Add Item')", strict=True)
        
        await page.wait_for_selector("li:has-text('Test Item')")
        
        items_count = await page.locator("li").count()
        assert items_count == 1
        
        await context.close()
        await browser.close()
