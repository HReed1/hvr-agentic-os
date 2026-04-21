# Executor Ephemeral Handoff Ledger 

**Purpose**: The Executor operates in a strict Ephemeral Amnesia mode, shedding all conversation context between directives to prevent token-bloat and tool-hallucination. 
**Directive**: **If you are the Executor**, you MUST proactively read this ledger before taking any action. It contains the most vital rules discovered in prior sessions that you must NOT repeat.

---

### TDAID & Testing Mechanics
* **Test Isolation Mechanism:** When drafting a new file that requires validation per the TDAID mandate, always write the test file to `tests/` first to establish the Red baseline before implementing the fix. Both the structural mutation and the test must be authored in the same session.
* **Staging Sandbox Overwrites:** `write_workspace_file` fails if the file exists in the workspace but not in `.staging/`; use `replace_workspace_file_content` with identical target/replacement strings to force staging even if content is identical. Ensure you don't execute redundant text overwrites.
* **Test Client Pathing / Discovery:** When testing staged mutations in an ephemeral airlock, prepend the `.staging` directory to `sys.path`. When standard pathing fails to shadow a package, use `importlib.util` to explicitly load the staged file and manually inject it into `sys.modules` using the package relative name (e.g. `sys.modules["api.main"]`).
* **Test Directory Initialization:** If `.staging/` is missing entirely in the root context, use `execute_transient_docker_sandbox` with `mkdir -p .staging` before attempting workflows dependent on promotion audits.
* **Database Dependency Decoupling:** For testing isolated infrastructure routes (like `/ping`), initialize `TestClient` directly from the injected application object `app` rather than `conftest.py` fixtures. This decouples database connections and prevents `OperationalError` when testing logic that doesn't need DB access.
* **Pytest Fixture Discovery:** Avoid explicit imports of fixtures (`from tests.conftest import client`). Rely on Pytest's automatic fixture discovery. If shadowing occurs, manually inject the modules and explicit imports.

### FastAPI & Backend Architecture
* **Async Engine Requirements:** SQLAlchemy 2.0 async engine configuration must explicitly use `postgresql+asyncpg://` URI scheme for `create_async_engine` (or `sqlite+aiosqlite://` for memory tests). Synchronous `psycopg2` drivers will fatally crash the pipeline.
* **Session Lifecycle:** `async_sessionmaker` replaces the legacy `sessionmaker`. Configure it with `expire_on_commit=False`. When migrating, wrap session generation in an `async` generator (`async with`) for proper dependency injection.
* **Route Organization:** When drafting new FastAPI endpoints, place routing logic strictly in `api/routers/`. Do not hallucinate novel package hierarchies like `api/endpoints/`. Ensure the router prefix is included explicitly in `api/main.py`.
* **Deep Eager Loading:** When returning heavy relational queries, use deep eager loading (`.options(selectinload(...))`) natively to prevent N+1 degradation patterns.

### Nextflow Orchestration Guardrails
* **Process Rules:** Nextflow DSL2 process blocks must be defined at the top level, explicitly outside of `workflow` blocks for structural integrity.
* **File Operations Limit:** Strictly avoid `samtools cat` for merging logic and `path(..., optional: true)` parameterizations, as they break our orchestration determinism boundaries.
* **Debugging Standard:** Nextflow DSL2 suppresses native process `stdout`. Use the `.view()` operator or `debug true` to expose terminal output for programmatic testing.

### Infrastructure-as-Code & Zero-Trust
* **Launch Template Bindings:** When drafting HCL for AWS Batch `aws_launch_template`, NEVER use the static `version = "$Latest"` string, as this causes internal State Drift traps. Use dynamic traversal attributes (`latest_version`).
* **IAM Least-Privilege Role Bifurcation:** Ensure task-specific execution boundaries by moving custom policies away from the host-level (EC2 Instance) down onto the task-level (ECS Task) roles to enforce Zero-Trust scoping.
* **Authentication Boundary:** Deprecate insecure static passwords or token checks from backend systems. Auth0 JWT validation `Depends(verify_token)` is the mandated structural boundary for all user REST execution logic.


### Refactoring Lessons: Cyclomatic Complexity Reduction
* **Dispatch Mapping:** Structural flattening of nested conditionals via `dispatch_map` significantly reduces McCabe scores.
* **Helper Decomposition:** Extracting leaf-level logic into discrete helper functions isolates branch complexity, ensuring the main entry point remains ≤ 5.
