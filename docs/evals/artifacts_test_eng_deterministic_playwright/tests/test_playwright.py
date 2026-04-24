import pytest
import time
import requests
import os
import sys
import multiprocessing
import uvicorn
from playwright.sync_api import sync_playwright

def run_server():
    sys.path.insert(0, os.path.abspath("."))
    uvicorn.run("main:app", host="127.0.0.1", port=8000)

def wait_for_server():
    for _ in range(50):
        try:
            r = requests.get("http://127.0.0.1:8000/")
            if r.status_code in (200, 404, 500):
                return True
        except Exception:
            pass
        time.sleep(0.1)
    return False

@pytest.fixture(scope="session", autouse=True)
def boot_server():
    server = multiprocessing.Process(target=run_server)
    server.start()
    
    if not wait_for_server():
        server.terminate()
        raise RuntimeError("Uvicorn failed to bind")
        
    yield
    
    server.terminate()
    server.join()
    
    if os.path.exists("app.db"):
        os.remove("app.db")

def test_add_item_crud():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="videos/",
            record_video_size={"width": 640, "height": 480}
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        
        page.goto("http://127.0.0.1:8000/")
        page.get_by_role("button", name="Add Item").click()
        
        context.tracing.stop(path="trace.zip")
        context.close()
        browser.close()