import multiprocessing
import os
import time
import pytest
import requests
from playwright.sync_api import sync_playwright
import uvicorn

def run_server():
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, log_level="error")

def wait_for_server(url: str, timeout: int = 10) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(url).status_code in (200, 404):
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False

@pytest.fixture(scope="session", autouse=True)
def boot_server():
    proc = multiprocessing.Process(target=run_server)
    proc.start()
    if not wait_for_server("http://127.0.0.1:8000/"):
        proc.terminate()
        raise RuntimeError("Uvicorn failed to bind")
    yield
    proc.terminate()
    proc.join()

@pytest.fixture(autouse=True)
def cleanup_db():
    yield
    if os.path.exists("app.db"):
        os.remove("app.db")

def test_add_item_crud():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            record_video_dir="videos/",
            record_video_size={"width": 800, "height": 600}
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        page = context.new_page()
        response = page.goto("http://127.0.0.1:8000/items")
        
        assert response and response.status == 200, "Route /items not implemented"
        
        page.fill("input[name='item_name']", "Test Item")
        page.click("button:has-text('Add Item')")
        
        page.wait_for_selector("text='Test Item'")
        
        context.tracing.stop(path="trace.zip")
        browser.close()
