import os
import sys
import time
import pytest
import multiprocessing
import requests
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

TEST_DB = f"sqlite+aiosqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_kanban.db'))}"

def run_server():
    os.environ["DB_PATH"] = TEST_DB
    import uvicorn
    from bin.launch_kanban import app
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

def wait_for_server(url: str, timeout: int = 15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    raise Exception("Server failed to bind")

@pytest.fixture(scope="module")
def local_server():
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_kanban.db'))
    if os.path.exists(db_file):
        os.remove(db_file)
        
    p = multiprocessing.Process(target=run_server)
    p.start()
    
    url = "http://127.0.0.1:8001/"
    wait_for_server(url)
    
    yield url
    
    p.terminate()
    p.join()
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except:
            pass

def test_kanban_e2e(local_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto(local_server)
        
        page.wait_for_selector("text=To Do")
        page.wait_for_selector("text=Doing")
        page.wait_for_selector("text=Done")
        
        add_task_btns = page.locator("button:has-text('+')")
        add_task_btns.nth(0).click()
        
        page.wait_for_selector("#modalTask", state="visible")
        
        page.fill("data-testid=task-title-input", "Buy Groceries")
        page.fill("data-testid=task-desc-input", "Milk, Eggs, Bread")
        page.fill("data-testid=task-tags-input", "shopping")
        
        page.click("data-testid=save-task-btn")
        
        page.wait_for_selector("#modalTask", state="hidden")
        
        page.wait_for_selector(".task", state="visible")
        
        page.locator(".task", has_text="Buy Groceries").click()
        page.wait_for_selector("#modalTaskDetail", state="visible")
        
        assert page.locator("data-testid=detail-title").text_content() == "Buy Groceries"
        assert page.locator("data-testid=detail-desc").text_content() == "Milk, Eggs, Bread"
        assert page.locator("data-testid=detail-tags").text_content() == "shopping"
        
        page.click("data-testid=close-detail-btn")
        page.wait_for_selector("#modalTaskDetail", state="hidden")
        
        source = page.locator(".task", has_text="Buy Groceries")
        target_list = page.locator("data-testid=task-list-2")
        
        source.drag_to(target_list)
        
        page.reload()
        page.wait_for_selector(".task", state="visible")
        
        task_in_col2 = page.locator("data-testid=task-list-2").locator(".task", has_text="Buy Groceries")
        assert task_in_col2.count() == 1
        
        browser.close()