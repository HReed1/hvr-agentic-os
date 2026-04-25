import os
import time
import pytest
import requests
import multiprocessing
import uvicorn
from playwright.sync_api import sync_playwright

DB_PATH = "app.db"

def run_server():
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, log_level="critical")

def wait_for_server():
    for _ in range(30):
        try:
            r = requests.get("http://127.0.0.1:8000/live")
            if r.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False

@pytest.fixture(scope="session", autouse=True)
def boot_server():
    # Teardown any dirty state before
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    proc = multiprocessing.Process(target=run_server)
    proc.start()
    
    if not wait_for_server():
        proc.terminate()
        raise RuntimeError("Uvicorn failed to bind within the polling window (ERR_CONNECTION_REFUSED)")
        
    yield
    
    proc.terminate()
    proc.join()
    
    # ENFORCED: Deterministic teardown anti-pattern to unlink DB locally
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_add_item_strict_mode():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Configure Playwright to output UI traces and volumetric video assets
        context = browser.new_context(
            record_video_dir="videos/",
            record_video_size={"width": 1280, "height": 720}
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        page = context.new_page()
        
        try:
            page.goto("http://127.0.0.1:8000/")
            # Strict mode verification for "Add Item" button
            page.locator("button:has-text('Add Item')").click(strict=True)
        finally:
            context.tracing.stop(path="trace.zip")
            context.close()
            browser.close()
