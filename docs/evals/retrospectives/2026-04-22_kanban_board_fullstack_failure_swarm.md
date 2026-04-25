# Retrospective: Kanban Board Full-Stack Development

## Initial Goal
The objective was to engineer a native, full-stack Kanban Board application confined strictly to the sandboxed Zero-Trust architecture. The requirements explicitly requested:
1. **Database Schema**: Purely asynchronous SQLAlchemy 2.0 ORM models for `Board`, `Column`, and `Task`.
2. **FastAPI Protocol**: Asynchronous HTTP routes supporting CRUD operations and a recursive state fetch for the board.
3. **DOM Client**: A vanilla HTML/CSS frontend with native HTML5 Drag and Drop, premium glassmorphism aesthetics, and custom DOM modals (strictly prohibiting native browser prompts).
4. **App Launcher**: A standalone `launch_kanban.py` script that seeds initial database state and dynamically maps static assets.
5. **Testing Crucible**: An End-to-End `pytest-playwright` test suite utilizing a localized Uvicorn background fixture with a polling readiness loop.

## Technical Hurdles Encountered
1. **Persistent Test State Interference**: The Executor's Playwright test failed due to a strict mode violation (`Locator.drag_to: Error: strict mode violation... resolved to 2 elements`). The SQLite database (`kanban.db`) persisted state across test executions, causing subsequent task creations to spawn duplicate elements in the DOM. Playwright's strict locators failed when finding multiple `"End-to-End Test Task"` nodes.
2. **Subprocess Coverage Decoupling**: The test suite invoked `subprocess.Popen()` to spawn the background Uvicorn server. Since the API routes ran in a detached child process, the Pytest coverage runner (`coverage.py`) completely failed to trace the backend execution paths, resulting in a 0% structural coverage report. 
3. **Unsafe Security Primitives**: The `subprocess.Popen` implementation was flagged natively by the QA Engineer's structural audit as a `[SECURITY VIOLATION]`, complicating the background fixture requirement.

## Ultimate Resolution / Failure State
**Execution State: FAILURE**

The loop failed and escalated after the `QA Engineer` issued a `[QA REJECTED]` termination. While the Executor successfully authored the codebase, passed the structural cyclomatic complexity audit (Max Score: 3, successfully under the <= 5 limit), and generated a beautifully structured DOM client, the execution was rejected. The failure was fundamentally rooted in test execution architecture: the inability to isolate the database state between test runs caused critical locator failures, and the reliance on an un-instrumented subprocess for the local server rendered the coverage requirements unfulfillable. The swarm was halted, escalating the need for native `TestClient` integration and deterministic DB teardowns.