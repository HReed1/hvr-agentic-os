import os
import subprocess
import time
import requests
import pytest

DB_PATH = "app.db"

@pytest.fixture(scope="function", autouse=True)
def db_teardown():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except OSError:
            pass
            
    import app
    app.init_db()
    
    yield
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except OSError:
            pass

@pytest.fixture(scope="session", autouse=True)
def boot_server():
    log_file = open("uvicorn.log", "w")
    server = subprocess.Popen(
        ["uvicorn", "app:app", "--port", "8000"],
        stdout=log_file,
        stderr=subprocess.STDOUT
    )
    
    max_retries = 20
    ready = False
    for i in range(max_retries):
        if server.poll() is not None:
            raise RuntimeError(f"Uvicorn crashed with exit code {server.poll()}")
        try:
            r = requests.get("http://localhost:8000/")
            if r.status_code in (200, 404):
                ready = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
            
    if not ready:
        server.kill()
        log_file.close()
        raise RuntimeError("Uvicorn failed to bind within the polling window (ERR_CONNECTION_REFUSED)")
        
    yield
    server.kill()
    log_file.close()

def test_add_item(page):
    page.goto("http://localhost:8000/")
    page.click("text=Add Item", strict=True)
