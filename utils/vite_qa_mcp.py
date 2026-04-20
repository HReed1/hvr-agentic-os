import os
import subprocess
import hmac
import hashlib
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vite QA Suite")

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

def _write_qa_signature():
    """Write HMAC cryptographic signature to .staging/.qa_signature on successful test pass."""
    staging_dir = os.path.join(project_root, ".staging")
    os.makedirs(staging_dir, exist_ok=True)
    sig = hmac.new(b"NGS_ZERO_TRUST_SIMULATION_KEY_2026", b"QA_PASSED", hashlib.sha256).hexdigest()
    with open(os.path.join(staging_dir, ".qa_signature"), "w") as f:
        f.write(sig)

def get_ui_dir():
    """Lazily evaluates target directory and auto-links node_modules inside staging so npx succeeds."""
    staging_ui = os.path.join(project_root, ".staging", "ngs-variant-ui")
    if os.path.exists(staging_ui):
        base_node_modules = os.path.join(project_root, "ngs-variant-ui", "node_modules")
        staged_node_modules = os.path.join(staging_ui, "node_modules")
        
        # Link node_modules inside the staged UI folder to fix Vite dependencies
        if os.path.exists(base_node_modules) and not os.path.exists(staged_node_modules):
            try:
                os.symlink(base_node_modules, staged_node_modules)
            except Exception:
                pass
                
        return staging_ui
    return os.path.join(project_root, "ngs-variant-ui")

@mcp.tool()
async def capture_ui_screenshot(route: str = "/") -> str:
    """
    Linked to skill: @vite-reactor-suite
    Natively opens a headless chromium browser and screenshots the Vite local server targeting the given route.
    """
    from playwright.async_api import async_playwright
    
    url = f"http://localhost:5173{route}"
    target_path = os.path.join(project_root, ".staging")
    if not os.path.exists(target_path):
        target_path = project_root
        
    img_path = os.path.join(target_path, "vite_reactor_screenshot_context.png")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=15000)
            await page.screenshot(path=img_path)
            await browser.close()
            
        return f"[SUCCESS] A physical screenshot of {route} has been mapped to: {img_path}."
    except Exception as e:
        return f"[FAILED] Playwright unable to snapshot the DOM: {str(e)}"

@mcp.tool()
def run_vitest_evaluation(pattern: str = "") -> str:
    """
    Linked to skill: @vite-reactor-suite
    Executes a Vitest unit/integration test natively. 
    Pattern must be relative to the ngs-variant-ui/ directory.
    """
    cmd = ["npx", "vitest", "run"]
    if pattern:
        prefixes_to_strip = [".staging/ngs-variant-ui/", "ngs-variant-ui/", ".staging/"]
        normalized = pattern
        for prefix in prefixes_to_strip:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
                break
        cmd.append(normalized)
        
    try:
        result = subprocess.run(cmd, cwd=get_ui_dir(), capture_output=True, text=True, timeout=120)
        output = result.stdout + "\n" + result.stderr
        output_limit = 2000
        if result.returncode == 0:
            _write_qa_signature()
            return f"[SUCCESS] Vitest Evaluated Cleanly.\n{output[-output_limit:]}"
        else:
            return f"[FAILED] Vitest Errors Detected:\n{output[-output_limit:]}"
    except Exception as e:
        return f"Error executing vitest: {str(e)}"

@mcp.tool()
def evaluate_typescript_diagnostics() -> str:
    """
    Linked to skill: @vite-reactor-suite
    Executes 'npx tsc --noEmit' in the front-end to rigorously validate TSX typings.
    """
    try:
        result = subprocess.run(["npx", "tsc", "--noEmit"], cwd=get_ui_dir(), capture_output=True, text=True, timeout=60)
        output_limit = 5000
        output = result.stdout + "\n" + result.stderr
        if result.returncode == 0:
            return "[SUCCESS] TypeScript Validation Passed.\n" + output[-output_limit:]
        else:
            return f"[FAILED] TypeScript Compilation Errors:\n{output[-output_limit:]}"
    except Exception as e:
        return f"Error executing typescript compiler: {str(e)}"

@mcp.tool()
def audit_eslint_glassmorphism(target_file: str = ".") -> str:
    """
    Linked to skill: @vite-reactor-suite
    Runs ESLint against a target file or wildcard path inside ngs-variant-ui.
    """
    try:
        result = subprocess.run(["npx", "eslint", target_file], cwd=get_ui_dir(), capture_output=True, text=True, timeout=60)
        output_limit = 2000
        output = result.stdout + "\n" + result.stderr
        if result.returncode == 0:
            return "[SUCCESS] ESLint Validation Passed."
        else:
            return f"[FAILED] ESLint Validation Errors:\n{output[-output_limit:]}"
    except Exception as e:
        return f"Error executing eslint: {str(e)}"

@mcp.tool()
async def playwright_evaluate_interaction(route: str, action: str, selector: str) -> str:
    """
    Linked to skill: @vite-reactor-suite
    Executes a direct DOM interaction upon a specific CSS selector using Headless Chromium.
    """
    from playwright.async_api import async_playwright
    
    url = f"http://localhost:5173{route}"
    target_path = os.path.join(project_root, ".staging")
    if not os.path.exists(target_path):
        target_path = project_root
        
    img_path = os.path.join(target_path, "vite_reactor_interaction_context.png")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            if action == 'click':
                await page.click(selector, timeout=5000)
            elif action == 'hover':
                await page.hover(selector, timeout=5000)
            elif action == 'fill':
                await page.fill(selector, "Test Payload", timeout=5000)
            else:
                await browser.close()
                return f"[ERROR] Action '{action}' is not supported."
                
            await page.wait_for_timeout(1000)
            await page.screenshot(path=img_path)
            await browser.close()
            
        return f"[SUCCESS] '{action}' executed. Screenshot: {img_path}."
    except Exception as e:
        return f"[FAILED] Playwright interaction failed: {str(e)}"

import re

@mcp.tool()
def provision_ui_dependency(package_name: str) -> str:
    """
    Linked to skill: @vite-reactor-suite
    Safely installs a specified NPM package into the environment. 
    """
    if not re.match(r'^@?[a-z0-9][a-z0-9\-\.\_]*(\/[a-z0-9][a-z0-9\-\.\_]*)?$|^[a-z0-9][a-z0-9\-\.\_]*$', package_name):
        return f"[FAILED] Package name '{package_name}' failed Zero-Trust regex validation."
        
    try:
        result = subprocess.run(["npm", "install", package_name], cwd=get_ui_dir(), capture_output=True, text=True, timeout=120)
        output_limit = 2000
        output = result.stdout + "\n" + result.stderr
        if result.returncode == 0:
            return f"[SUCCESS] Package '{package_name}' installed."
        else:
            return f"[FAILED] NPM Installation failed:\n{output[-output_limit:]}"
    except Exception as e:
        return f"Error executing NPM provisioning: {str(e)}"

if __name__ == "__main__":
    mcp.run()
