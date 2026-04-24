# Full-Stack Benchmark Implementation Walkthrough

The "God-Mode" stress-testing benchmark has been natively wired into the framework. This capability empowers you to definitively measure whether dropping hierarchical routing causes catastrophic hallucination loops when evaluating complex multi-file application scaffolding. 

## 1. The Crucible Payload
`tests/comparisons/test_compare_fullstack.test.json` now exists. The deeply mapped `[EVALUATOR_CRITERIA]` forces both versions of the agent to author:
- `api/models_kanban.py` with SQLAlchemy nested foreign keys.
- `api/routers/kanban.py` mapped to the primary FastAPI server.
- `api/templates/kanban.html` executing fetch endpoints against the router.
- `tests/test_kanban_fullstack.py` achieving >= 80% line coverage executing `sqlite+aiosqlite:///:memory:` against the SQLite backend.

## 2. Telemetry Aggregation Map
 `utils/generate_comparison_report.py` has been explicitly scaled. The `test_compare_fullstack` key was added to the aggregation pipeline parsing `.adk/` caching results and plotting them strictly downstream into the native `HEAD_TO_HEAD_SCORECARD.md`.

## 3. The Isolated Execution Script
`run_kanban_benchmark.sh` has been duplicated natively from `run_head_to_head.sh`. It enforces exactly the same Amnesia Sweep logic, Memory Bridging, and pipeline executions as the primary loop, but it explicitly targets ONLY `tests/comparisons/test_compare_fullstack.test.json` so you do not burn massive tokens waiting for the smaller payloads to evaluate.

The script is marked executable (`chmod +x bin/run_kanban_benchmark.sh`). 

### How to Evaluate
1. Launch `./bin/run_kanban_benchmark.sh` to begin tracking inference execution.
2. Watch the output stream to observe `solo_agent` handling the intense context window logic vs the Swarm seamlessly compartmentalizing the database syntax testing! 
3. When it is complete, review `docs/comparisons/HEAD_TO_HEAD_SCORECARD.md` to see exactly who won.
