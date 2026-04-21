# ADK Open-Source Pipeline & Future Monkeypatch Forks

*Date: 2026-04-21*

This retrospective serves as the official compilation map for structural patches made against the `google-adk` framework dependency. If and when we officially fork `google-adk` out of the virtual environment to assume absolute Zero-Trust pipeline control over telemetry rendering and architecture loops, these structural constraints MUST be patched native to the OS.

## 1. Global Crawler Path Injection (`No root_agent`)
**The Issue:** Running `adk web` from the project root scans *every* directory for an active `root_agent` map.
**The Vulnerability:** `adk web` is capable of dynamically corrupting sub-directories like `/plugins` by aggressively generating ghost `.adk/session.db` folders inside them natively during the scan. Once this drop happens, the backend fatally enters a caching crash loop if that namespace is ever queried by the frontend React app.
**The Fix:** 
- Natively restrict the recursive glob search in `google/adk/cli/utils/agent_loader.py` to only explicitly configured `.env` directories.
- Refuse to write `.adk` SQLite layers if `root_agent.yaml` or an explicit `BaseAgent` Python hook cannot be physically proven.

## 2. Environment Variable Segregation on Subprocesses
**The Issue:** Custom environment variables like `EVALUATING_TEST_NAME` bind smoothly via standard TDAID Bash loops, but when piped through `adk run`, `invoke_run()` drops OS-level shell bindings before transferring execution bounds to the python daemon process.
**The Vulnerability:** Extracted traces completely lose associative test mapping context.
**The Fix:**
- Fork `google/adk/cli/invoke.py` or `.adk_runner` to explicitly allow a `--env-passdown` hook or `dict` expansion mimicking `subprocess.Popen(env=os.environ.copy())`.

## 3. Evaluation Namespace Masking (`___eval___session___`)
**The Issue:** The React Dev UI actively restricts the rendering of headless background evaluations by dynamically querying against `startswith("___eval___session___")`.
**The Vulnerability:** Teams utilizing headless CI/CD evaluation scripts are structurally locked out of viewing their interactive graphs unless they physically inject the raw JSON back through the ADK Eval Set mechanism inside the UI.
**The Temporary Monkeypatch:** We utilize a custom `bin/adk-trace-importer.py` cron job to duplicate the payload directly into SQLite inside `agent_app/.adk/session.db` removing the `EVAL_SESSION_ID_PREFIX`.
**The Fix:** 
- Expose a `Show Evaluation Traces` dashboard toggle internally inside `google/adk/cli/adk_web_server.py:list_sessions()`.

## 4. UI Relative Namespace Mapping Broken by Symlinks
**The Issue:** Attempting to securely isolate `/agent_app` via symlinks (`adk_apps/agent_app`) to avoid the global crawler logic shatters the absolute path mappings natively stored in SQLite `events` and `.eval_history` metrics. 
**The Vulnerability:** Sessions decouple from their corresponding traces resulting in blacked-out browser screens.
**The Fix:**
- Enforce explicit configuration paths via `adk web --app-roots=agent_app` natively inside the Python click arguments, dropping the implicit relative hierarchy assumption altogether.

## 5. Hallucinated Tool Crash Hook (`_patched_get_tool`)
**The Issue:** When testing LLMs hallucinate tools that aren't structurally registered in their array, ADK violently throws a `ValueError: Tool not found`, causing an unrecoverable 500 error cascade that vaporizes the evaluation session.
**The Temporary Monkeypatch:** In `agent_app/zero_trust.py`, we override `adk_llm_functions._get_tool` to physically capture the `ValueError` and return a synthetic `FunctionTool` mimicking the bad name. This dynamically forces the LLM to process a `[ZERO-TRUST FRAMEWORK ERROR]` string and explicitly recover.
**The Fix:** 
- `google/adk/flows/llm_flows/functions.py` needs native try/except wrappers routing explicit `ToolNotFoundError` payloads natively backward to the LLM model context window instead of yielding to standard output.

## 6. Execution Loop Interceptor Hooks (`LoopAgent._run_async_impl`)
**The Issue:** `LoopAgent` implicitly trusts all LLM tool invocation streams perpetually without structural evaluation logic until token burnout or manual tool limits trigger.
**The Temporary Monkeypatch:** We completely replaced `_original_loop_run` to natively inject `_intercept_tool` middleware. This custom layer structurally catches system state tools (`mark_system_complete`, `approve_staging_qa`), parses `[QA REJECTED]` string anomalies, and violently throws `ZeroTrustEscalationEvent` if systemic bounds (`_consecutive_discovery >= 15`) are violated.
**The Fix:**
- ADK's `LoopAgent` must abstract a native `middleware` or `pre_tool_execution` pipeline architecture that allows developers to gracefully veto execution graphs and inject synthetic escalation events dynamically.

## 7. Data Loss Prevention & API Throttling (`LlmAgent._run_async_impl`)
**The Issue:** `google-adk` naturally allows unfiltered LLM payloads, is susceptible strictly to `RESOURCE_EXHAUSTED` (429) API quotas without generic backoff, and lacks dynamic context-window truncation.
**The Temporary Monkeypatch:** We heavily patched the LLM async loop, explicitly overriding `ctx.messages` dynamically to slide the context window down to the latest 7 messages under `CONTEXT_SAFE_MODE`. We intercept and pass all `part.text` through our `redact_genomic_phi` DLP algorithm and embed a sweeping exponential backoff loop natively catching `429` and `503` payloads.
**The Fix:**
- Expose global `data_scrubbing_middleware=Callable` directly on the root agent structure.
- Abstract configurable `api_retry_strategy` mappings inside the execution config parameter.

## 8. Evaluation Array Length Mapping (`LocalEvalService._evaluate_single_inference_result`)
**The Issue:** TDAID deterministic evaluation vectors expect specific event trace counts. When an LLM executes a perfectly correct operational flow but requires *more* tools than explicitly hardcoded in the TDAID bounds, ADK throws a fatal `OutOfBounds` exception while cross-mapping array boundaries inside `tool_trajectory_avg_score`.
**The Temporary Monkeypatch:** Our wrapper around the test parser (`padded_get_eval_case`) forcibly pads `eval_case.conversation.append(eval_case.conversation[-1])` dynamically based on native invocation traces to artificially stabilize the length array.
**The Fix:** 
- The metric parsing engine natively requires a `lenient_trajectory_match` configuration allowing temporal shifting rather than strict `len(a) == len(b)` failure conditions.

## 9. Default MCP Client Timeout Constraints (`ClientSession.__init__`)
**The Issue:** Deep-execution MCP Servers (like spinning up sandbox environments or parsing monolithic graphs natively) occasionally exceed standard read timeouts on the JSON-RPC socket, blowing up background evaluations.
**The Temporary Monkeypatch:** Monkeypatching the internal `mcp` SDK `ClientSession.__init__` explicitly enforcing `read_timeout_seconds = 600`.
**The Fix:** 
- Propagate a native `mcp_timeout_seconds` variable throughout the ADK MCP architecture mapping schemas.
