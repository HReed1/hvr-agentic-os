import os
import subprocess
import time
import requests
import pytest
import pytest_asyncio
from playwright.sync_api import Page, expect

def wait_for_server():
    for _ in range(20):
        try:
            r = requests.get("http://localhost:8000/")
            if r.status_code in (200, 404):
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False

@pytest_asyncio.fixture(scope="session", autouse=True)
def boot_server():
    server = subprocess.Popen(["uvicorn", "app.main:app", "--port", "8000"])
    if not wait_for_server():
        server.kill()
        raise RuntimeError("Uvicorn failed to bind within the polling window (ERR_CONNECTION_REFUSED)")
    yield
    server.kill()

@pytest.fixture(scope="function", autouse=True)
def db_teardown():
    yield
    if os.path.exists("app.db"):
        os.remove("app.db")

def test_add_item(page: Page):
    page.goto("http://localhost:8000/")
    page.click("text='Add Item'", strict=True)
    expect(page.locator("text='Item added'")).to_be_visible()