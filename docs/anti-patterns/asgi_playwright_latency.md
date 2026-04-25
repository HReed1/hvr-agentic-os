# Anti-Pattern: ASGI Playwright Test Latency (`ERR_CONNECTION_REFUSED`)

## The Paradox
When executing full-stack E2E Pytest suites using `@pytest_asyncio.fixture` to launch local web servers (e.g. Uvicorn, Hypercorn, FastAPI) as background `subprocess` threads alongside Playwright, Pytest routinely fails with `net::ERR_CONNECTION_REFUSED` or timeouts.

## The Cause
Playwright boots its headless Chromium instance natively in fractional milliseconds. However, Uvicorn takes up to `500ms` or `1s` to resolve host networking layers and successfully bind to `127.0.0.1:8000`. By the time Playwright attempts to `page.goto("http://localhost:8000")`, the server is physically unreachable, causing the test to falsely crash and implying your Pytest routing logic is flawed.

## The Mandated Solution (Polling Loop)
You MUST NOT alter the backend routing logic to fix this testing race condition. Instead, you MUST inject a strict synchronous socket/readiness polling loop block natively into the testing module BEFORE yielding control to Playwright.

### Example Correct Usage:

```python
import subprocess
import time
import requests
import pytest
import pytest_asyncio

@pytest_asyncio.fixture(scope="session", autouse=True)
def boot_server():
    server = subprocess.Popen(["uvicorn", "api.main:app", "--port", "8000"])
    
    # REQUIRED: Active Polling Architecture
    max_retries = 20
    ready = False
    for i in range(max_retries):
        try:
            r = requests.get("http://localhost:8000/") # Or any root path
            if r.status_code == 200 or r.status_code == 404: # Even a 404 means the server bound successfully!
                ready = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
            
    if not ready:
        server.kill()
        raise RuntimeError("Uvicorn failed to bind within the polling window (ERR_CONNECTION_REFUSED)")
        
    yield
    server.kill()
```
