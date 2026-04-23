import subprocess
import time
import requests
import pytest
import os
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session", autouse=True)
def manage_db_state():
    if os.path.exists("app.db"):
        os.remove("app.db")
    yield
    if os.path.exists("app.db"):
        os.remove("app.db")

def wait_for_server(url="http://localhost:8000/", max_retries=20):
    for _ in range(max_retries):
        try:
            r = requests.get(url)
            if r.status_code in (200, 404):
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False

@pytest.fixture(scope="session", autouse=True)
def boot_server(manage_db_state):
    server = subprocess.Popen(["uvicorn", "api.main:app", "--port", "8000"])
    
    if not wait_for_server():
        server.kill()
        raise RuntimeError("Uvicorn failed to bind within the polling window")
        
    yield
    server.kill()

def test_add_item(boot_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="test-results/videos/"
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        page = context.new_page()
        page.goto("http://localhost:8000/")
        
        page.fill("#itemName", "Test Item")
        page.locator("#addItemBtn").click()
        
        page.wait_for_selector("text=Test Item")
        assert page.locator("li").filter(has_text="Test Item").count() == 1
        
        context.tracing.stop(path="test-results/trace.zip")
        context.close()
        browser.close()
