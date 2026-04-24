# Walkthrough: The Head-To-Head Evaluator
The architecture required to systematically compare a "God-Mode" Solo LLM against the multi-agent `autonomous_swarm` is fully mapped and operational. 

## 1. Zero-Trust Bound Solo Routing
The native `agent_app/__init__.py` interface now accepts an overridden `ADK_SWARM_MODE=solo` environment hook.

When triggered, it dynamically loads the monolithic `solo_agent` explicitly defined in `agent_app/agents.py`. The agent has been instantiated using identical `McpToolset` standard IO bindings as the swarm. This guarantees that its access to `promote_staging_area` inherently triggers the `bin/dlp-firewall`, keeping the benchmarking constraints fair across the board without sacrificing the Zero-Trust mandate. 

## 2. Test Matrix Synthesis
We successfully generated 3 tiered scale evaluation matrices inside `tests/comparisons/`:
- **test_compare_small.test.json**: Write 2 math functions and 100% Pytest coverage to baseline the inference latency jump.
- **test_compare_medium.test.json**: Architect a dynamic CSV parsing class natively aware of edge-case exceptions (`FileNotFoundError`), with Pytest thresholds evaluating successful structural deployment.
- **test_compare_large.test.json**: Conduct a destructive refactor of an abstract procedural API boundary leveraging polymorphic dispatch routing. Validating that structural Cyclomatic Complexity matrices map dynamically against unit test verification. 

## 3. Telemetry & Bash Orchestration
The new execution script `bin/run_head_to_head.sh` accepts no arguments. When run, it:
1. Iterates completely through the 3 comparison tests.
2. For each test, it executes the Swarm payload via `adk eval`, extracts telemetry traces synchronously with `utils/inject_telemetry.py`, triggers the amnesia sweep, then seamlessly transitions cleanly into the Solo evaluation run.
3. At the end of the loop, the `utils/generate_comparison_report.py` executes, natively formatting a unified data model into `docs/comparisons/HEAD_TO_HEAD_SCORECARD.md` listing the precise Tokens IN/OUT thresholds across models!

You are officially ready for telemetry benchmarking!
