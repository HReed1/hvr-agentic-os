# Retrospective: Resolving ADK Headless Telemetry Isolation & Observability

*Date: 2026-04-21*

## Executive Summary
**Goal:** Restore physical visibility of headless Swarm CI/CD evaluation traces (`TDAID`) internally inside the interactive React Agent Development Kit (ADK) dashboard.
**Result:** SUCCESS
**Impact:** Swarm Engineers can now instantly view complex multi-agent execution geometries, tool outputs, and LLM latency traces dynamically without having to halt evaluation runners or manually reverse-engineer raw JSON dumps.

## Architecture Breakdown

### The Contextual Isolation Paradox
While building our Zero-Trust TDAID pipelines natively on top of the `.test.json` CI/CD evaluation runner (`run_all_evals.sh`), all temporal execution telemetry was seamlessly written to `agent_app/.adk/eval_history/*`. However, the ADK UI persistently rendered an empty "Select a Session" matrix when the test engineer physically tried to inspect their runs. 

### The Root Cause 
Through deep architectural analysis into the `google-adk` backend FASTAPI daemon (`venv/lib/python3.14/site-packages/google/adk/cli/adk_web_server.py`), we discovered the framework was intentionally locking out any execution trace prefixed with `___eval___session___` from being parsed by the `list_sessions()` endpoint.

### The Organic Bridge (Trace Importer)
Instead of executing a chaotic monkeypatch on the compiled Node/Vite PIP package—which would evaporate upon the next installation—we engineered a hermetic pipeline: `bin/adk-trace-importer.py`. 
- **The Pipeline:** The script statically extracts the raw matrix arrays from the physical `.eval_history` JSON cache. It systematically bypasses the `EVAL_SESSION_ID_PREFIX` blocklist by renaming the evaluation traces to `evaltrace_...` and physically merging them via a structurally perfect SQLite insertion into `user` namespace on `session.db`. 
- **The Magic:** Bypassing the FastApi backend natively forces the React frontend to magically visualize headless CI runs seamlessly as if they were live interactive developer sessions!

## Automating UI Interpolation (MCP Protocol)
To permanently cement this knowledge physically inside the Swarm's neural map:
1. We authored `@mcp.tool() def import_eval_traces()` on the `adk-trace-reader` MCP server automating the script invocation natively in python.
2. We codified instructions into the `adk-trace-animator` **Skill** authorizing any internal QA framework Agent to autonomously fire the bridging protocol the exact second a user declares: *"Load my traces into the UI."*

## Next Steps
In tandem with resolving nested evaluation masks, we documented and cataloged all internal architectural pipeline vulnerabilities caused by `google-adk` natively traversing the file tree (the `plugins` root conflict, symlink crashes, and OS-bound environment variable leaks). This framework anomaly mapping resides entirely at `docs/retrospectives/adk_fork_notes.md` to guarantee a flawless PR structure when the OS moves to isolate `google-adk` via a permanent fork.
