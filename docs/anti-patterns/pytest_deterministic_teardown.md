## Pytest Intra-Session State Pollution

**Context**: In multi-step evaluations, test runners like `execute_tdaid_test` and `execute_coverage_report` are executed sequentially across the same physical `.staging/` workspace. If database files (like SQLite `.db` stores) persist between these runs, subsequent E2E Playwright tests will fail due to Duplicate Data state accumulation breaking strict mode selectors.

**Anti-Pattern**:
- Developing `.fixture()` setups that create a testing database but fail to implement a proper teardown sequence to actively unlink or physically wipe the state locally.
- Assuming the overarching Swarm evaluation suite cleans the workspace between your local `QA Engineer` executions.

**Corrective Action**:
- You **MUST** ensure all standard backend and E2E Pytest structures feature teardown generators (`yield` teardowns) that physically remove the testing database (e.g., `os.remove(".staging/kanban.db")` or equivalent). 
- State MUST reset to zero before the next Pytest worker initializes to prevent `playwright._impl._api_types.Error: strict mode violation: resolved to 2 elements`.
