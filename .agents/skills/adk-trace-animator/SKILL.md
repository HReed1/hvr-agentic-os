---
name: adk-trace-animator
description: Automates native orchestration and visualization of agentic swarm execution traces from the SQLite database.
---

# ADK Trace Animator

**Purpose:** Provide the Swarm with seamless native visualization and telemetry mapping payloads without resorting to brittle bash, sqlite3, or terminal python invocations.

## When to use this skill
* When asked to analyze or visualize the recent progression of the swarm.
* When asked to generate an animation or interactive HTML map of a previous trace run.
* When explicitly asked to summarize the "latest session" operations.

## How to use it
* You must prioritize utilizing your native `adk-trace-reader` MCP server tools!
* **DO NOT** execute raw bash commands (like `sqlite3 agent_app/.adk/session.db ...`) or python sub-processes natively on the console CLI to evaluate traces.
* **Trace Parsing:** Use the `get_latest_adk_session` MCP tool to pull raw textual context. By default, it infers the most recent run, but you can explicitly pass a `session_id`.
* **Visual Graph Generation:** If a session visualization is requested, fire the `generate_session_animation` MCP tool to natively convert any session sequence into an interactive HTML visualization. You can pass it a `session_id` parameter, or call it with no parameters and it will safely default to tracing the latest execution.
* **UI Trace Importation:** If a headless CI/CD evaluation test has finished and the user demands to physically view the logic inside their "ADK Web React Dashboard" natively, fire the `import_eval_traces` MCP tool. This explicitly translates the hidden JSON structures bypassing Google-ADK constraints and inserts them as native sessions!
