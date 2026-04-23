---
name: playwright-engineer
description: Official guidelines, structural API bounds, and networking invariants for correctly writing robust AI-generated Playwright tests within the OS.
---

# Skill: Playwright Engineer

Modern E2E automation for AI Agents leverages Playwright’s robust browser control capabilities. However, due to systemic AI hallucination around Playwright's natively expanding API, the Swarm MUST aggressively enforce these documented best practices to prevent test collapse.

## 1. Locators & Strict Mode
Playwright enforces **strict mode** uniformly by default. The test will crash if a locator unexpectedly finds two elements (e.g. `Error: strict mode violation: resolved to 2 elements`). 

- **Do NOT hallucinate Pytest explicit keywords**: Playwright python does **NOT** contain a `strict=True` keyword argument for actions like `.click()`. Attempting `page.locator(".btn").click(strict=True)` throws a fatal `TypeError`.
- **User-Centric Locators First**: The Swarm MUST favor user-centric role locators over CSS strings where possible. E.g., leverage `page.get_by_role("button", name="Submit")` instead of `page.locator(".btn")`.
- **Positional Bypassing**: When structurally dealing with identical dynamic UI collections (like standard list inputs) where `strict` is organically violated, structurally bypass it natively via positional indexing:
  - `page.locator(".btn").first.click()`
  - `page.locator(".btn").nth(1).click()`
- **Chaining Locators**: Rather than bypassing strict mode immediately, attempt to organically isolate elements using chained structural paths (e.g., `page.locator("#my-div").get_by_role("button")`).

## 2. API Network Determinsim
To ensure robust interaction loops, minimize manual timeouts and stabilize Uvicorn.
- **Auto-Wait Paradigms**: Never utilize `time.sleep()`. Aggressively favor Playwright's internal asynchronous `wait` handlers or `.to_be_visible()` validations native to `expect(locator)`. Wait-states are resolved organically.
- **Localhost Proxy Evasion**: When designing standard ASGI Uvicorn background fixture bootups (`subprocess.Popen`), the Swarm **MUST ALWAYS** bind the port explicitly using the literal string `--host localhost` (e.g., `http://localhost:8000`). Under NO circumstances should the Swarm organically bind to the IPv4 address `127.0.0.1`. Numeric bindings overlap with the Zero-Trust system's Go RE2 DLP proxy and execute false-positive `<REDACTED_PHI>` trace kills. 
- **Cyclomatic Fixture Isolation**: Database un-linking schemas must be separated mechanically from Subprocess `Popen` setups within Pytest. Maintain complexity strictly $\le 5$.

## 3. Visual Cryptography & Tracing
UI testing mandates verifiable visual proof that organic logic accurately mutates the DOM interface natively. Static single screenshots are frequently insufficient to prove system animations, timing overlaps, or state lifecycles.
- **Protocol (Video & Traces)**: The Executor MUST configure Playwright contexts to automatically generate Videos and Traces recursively. Do NOT rely on single `page.screenshot()` executions.
- **Configuration Syntax**: 
  When booting the browser parameters, map the output explicitly to a vaulted `.staging/artifacts` payload destination:
  ```python
  context = browser.new_context(record_video_dir=".staging/artifacts/videos")
  context.tracing.start(screenshots=True, snapshots=True, sources=True)
  # ... (execute E2E validation script)
  context.tracing.stop(path=".staging/artifacts/trace.zip")
  ```
- **Amnesia Sweep Extraction**: Evaluation test pipelines leverage aggressive `git clean -fd` amnesia sweeps between test paradigms. By dumping traces and `mp4` bundles structurally within the `.staging/artifacts` folder, the bash environment will autonomously scan, index, and safely extract the visuals into `docs/comparisons/` completely organically before triggering the destruct sequence!
