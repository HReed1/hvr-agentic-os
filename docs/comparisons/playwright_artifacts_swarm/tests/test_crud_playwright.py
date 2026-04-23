import os
import subprocess
import time
import requests
import pytest
from playwright.async_api import async_playwright

DB_PATH = ".staging/app.db"

@pytest.fixture(scope="session", autouse=True)
def db_teardown():
    yield
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except OSError:
            pass

@pytest.fixture(scope="session", autouse=True)
def boot_server():
    server = subprocess.Popen(["uvicorn", "api.main:app", "--port", "8000"])
    
    max_retries = 50
    ready = False
    for i in range(max_retries):
        try:
            r = requests.get("http://127.0.0.1:8000/")
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

@pytest.mark.asyncio
async def test_add_item_strict_mode():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            record_video_dir=".staging/videos/",
            record_video_size={"width": 1280, "height": 720}
        )
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        page = await context.new_page()
        try:
            await page.goto("http://127.0.0.1:8000/")
            await page.click("text=Add Item", strict=True)
        finally:
            os.makedirs(".staging/traces/", exist_ok=True)
            await context.tracing.stop(path=".staging/traces/trace.zip")
            await browser.close()
