---
title: "Telemetry Engine"
date: 2026-06-02
category: entity
tags:
  - telemetry
  - monitoring
  - evaluation
  - sqlite
sources:
  - "[[docs/retrospectives/2026-04-20_zero_trust_stabilization_and_telemetry.md]]"
  - "[[docs/retrospectives/2026-04-24_context_caching_optimization_results.md]]"
last_ingested: 2026-06-02
---

# Telemetry Engine

The Telemetry Engine is a programmatic extraction and reporting subsystem for the [[agentic-os]] that navigates ADK trace databases and evaluation caches to map granular API inference metrics to evaluation reports.

## Architecture

### Trace Sources
- **SQLite `session.db`**: The primary ADK trace cache containing execution traces, tool calls, and agent inference records
- **`agent_app/.adk/eval_history/`**: JSON log cache from `adk eval` runs, used when SQLite trace limit conflicts occur due to `git wipe` loops

### Extraction Pipeline
The `utils/inject_telemetry.py` script programmatically extracts:
- Total LLM inferences per agent
- Input/output token counts
- Tool call sequences and parallelism patterns
- Looping thresholds and iteration counts

### Reporting
The `utils/generate_global_eval_report.py` script (refactored to ≤5 McCabe complexity per function) aggregates telemetry into the Global Evaluation Scorecard, with per-test breakdowns of inferences, tokens, and pass/fail status.

### ADK Session Animator
The `adk-trace-animator` skill provides visual orchestration and animation of swarm execution traces from the SQLite database.

## Hot-Patched Integration
The `write_eval_report` tool in `agent_app/tools.py` directly loads the latest `.evalset_result.json` before drafting evaluation documentation, enabling the Meta-Evaluator agent to autonomously inject granular telemetry metrics.

## See Also

- [[evaluation-framework]] — The benchmark infrastructure that generates trace data
- [[context-caching]] — Optimization measured through telemetry data
- [[agentic-os]] — The broader system being measured
