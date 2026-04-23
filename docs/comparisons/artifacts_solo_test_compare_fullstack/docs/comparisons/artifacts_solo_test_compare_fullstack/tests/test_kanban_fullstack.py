import pytest
import subprocess
import time
import requests
import os
import sys
from playwright.sync_api import sync_playwright, Page, expect

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(scope="module")
def server():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kanban.db"))
    if os.path.exists(db_path):
        os.remove(db_path)

    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    proc = subprocess.Popen(
        [sys.executable, "-m", "bin.launch_kanban"],
        env=env,
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    )
    
    ready = False
    for _ in range(40):
        try:
            res = requests.get("http://127.0.0.1:8000/")
            if res.status_code == 200:
                ready = True
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.5)
    
    if not ready:
        proc.terminate()
        pytest.fail("Server did not start in time")
        
    yield
    proc.terminate()
    proc.wait()

def test_kanban_fullstack(server, page: Page):
    page.goto("http://127.0.0.1:8000/")
    
    expect(page.locator("text=To Do")).to_be_visible()
    expect(page.locator("text=Doing")).to_be_visible()
    expect(page.locator("text=Done")).to_be_visible()
    
    page.locator('.column').filter(has_text="To Do").locator('button', has_text='+').click()
    expect(page.locator('#task-modal')).to_be_visible()
    
    page.locator('#task-title').fill("Test Task")
    page.locator('#task-desc').fill("Task Description")
    page.locator('#task-tags').fill("test, e2e")
    page.locator('#btn-create-task').click()
    
    expect(page.locator('.task-title', has_text="Test Task")).to_be_visible()
    
    page.locator('.task').filter(has_text="Test Task").click()
    expect(page.locator('#detail-modal')).to_be_visible()
    expect(page.locator('#task-detail-title', has_text="Test Task")).to_be_visible()
    expect(page.locator('#task-detail-desc', has_text="Task Description")).to_be_visible()
    expect(page.locator('.tag', has_text="e2e")).to_be_visible()
    
    page.locator('#detail-modal').locator('button', has_text="Close").click()
    expect(page.locator('#detail-modal')).not_to_be_visible()
    
    page.locator('button', has_text="+ Add Column").click()
    expect(page.locator('#col-modal')).to_be_visible()
    page.locator('#col-name').fill("QA")
    page.locator('#col-modal').locator('button', has_text="Create").click()
    
    expect(page.locator('h2').filter(has_text="QA")).to_be_visible()

    task_el = page.locator('.task').filter(has_text="Test Task")
    drop_target = page.locator('.column').filter(has_text="Doing").locator('.task-list')
    task_el.drag_to(drop_target)
    
    time.sleep(1)
    doing_col = page.locator('.column').filter(has_text="Doing")
    expect(doing_col.locator('.task-title', has_text="Test Task")).to_be_visible()
    
    qa_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".qa_signature"))
    with open(qa_path, "w") as f:
        f.write("E2E tests passed successfully.")
