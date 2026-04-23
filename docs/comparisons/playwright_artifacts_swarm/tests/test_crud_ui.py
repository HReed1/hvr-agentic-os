import os
import time
import requests
import pytest
import multiprocessing
import uvicorn
from playwright.sync_api import Page, expect

def run_server():
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, log_level="info")

def wait_for_server(url="http://127.0.0.1:8000/", max_retries=20):
    for _ in range(max_retries):
        try:
            r = requests.get(url)
            if r.status_code in (200, 404):
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    return False

@pytest.fixture(scope="session", autouse=True)
def boot_server():
    db_path = "app.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    server = multiprocessing.Process(target=run_server)
    server.start()
    
    if not wait_for_server():
        server.terminate()
        server.join()
        raise RuntimeError("Uvicorn failed to bind within the polling window (ERR_CONNECTION_REFUSED)")
        
    yield
    
    server.terminate()
    server.join()
    if os.path.exists(db_path):
        os.remove(db_path)

def test_add_item(page: Page):
    page.goto("http://127.0.0.1:8000/")
    add_button = page.locator("button:has-text('Add Item')")
    add_button.click()
    item = page.locator(".item").last
    expect(item).to_be_visible()
