---
description: Workflows granting the Swarm the autonomy to diagnose and self-heal broken toolchain environments. Section 1 covers Python/Bash script degradation (Executor). Section 2 covers npm/Node.js dependency failures in the UI layer (QA Engineer).
---

# Agentic Self-Healing Workflow

## Section 1: Python/Bash Tool Degradation (Executor)

**Purpose**: The tools the Triad uses to manage Nextflow and AWS (e.g. `ssm-telemetry-suite`, `finops-pricing-oracle`) are static Python/Bash scripts. When external APIs change or AWS AMIs update, these scripts will break, blinding the Triad. This workflow delegates the responsibility to the AI itself.

### Workflow Execution Steps

1. **Detect Tool Degradation**: Recognize when a `run_command` invoking a local Triad script (e.g. `mcp_aws-batch-diagnostics_get_live_container_ram`) returns a stack trace or an unexpected data schema. Do not ignore the trace. **EXCEPTION:** If the failure originates from a DLP-restricted MCP Tool (like `aws-batch-diagnostics` or `ssm-telemetry-suite`), you must **halt**. You are explicitly forbidden from using `run_command` on the underlying Python/Bash script natively. Escalate the traceback directly to the Director.
2. **Read Script Payload**: Actively `view_file` the deprecated script to understand its logical intent and dependencies.
3. **Draft Self-Healing Pytest**: Author a TDAID Python test (`test_agentic_tool_patch.py`) targeting the isolated `utils/` script logic. Confirm the Pytest enters the Red State by reproducing the identical error seen in the cloud.
4. **Draft the Patch & Diff**: Copy the broken script to `tests/agent_workspace_tmp/`. Apply the fix in this temporary directory. Confirm the local Pytest flips to Green against the copied file.
5. **Halt and Output Diff**: Generate the resulting `.diff` block between the broken host script and your temporary fixed script. Print the diff string, and STOP. Inform the Director to physically apply the diff to `utils/` on the Host.

---

## Section 2: npm/Node.js Dependency Failures (QA Engineer)

**Purpose**: The React UI in `ngs-variant-ui` depends on npm packages that may be absent from `.staging/ngs-variant-ui/node_modules/` when the Executor stages a new component importing a previously unused library. A missing module produces `"Failed to resolve import"` or `"Cannot find module"` errors that cascade through the entire Vite toolchain, making unrelated tests appear to fail. This section defines the mandatory recovery sequence.

**Owner**: QA Engineer. The Executor does not touch `node_modules` or run `npm install`.

### Trigger Conditions

This workflow activates when ANY of the following appear in output from `evaluate_typescript_diagnostics`, `run_vitest_evaluation`, or the Vite dev server:

- `"Failed to resolve import"`
- `"Cannot find module"`
- `"import-analysis"`
- `"Module not found"`
- `"ERR_MODULE_NOT_FOUND"`

### Workflow Execution Steps

1. **Stop immediately.** Do not attempt to mock the missing module. Do not tell the Executor to re-check their import paths. Do not push through the error and continue testing.
2. **Identify the missing package**: Extract the exact package name from the error string (e.g., `"Cannot find module 'react-toastify'"` → package is `react-toastify`).
3. **Call `provision_ui_dependency`**: Pass the canonical npm package name. Wait for confirmed success output from the tool.
4. **Restart validation from the top**: After `provision_ui_dependency` confirms success, restart from `evaluate_typescript_diagnostics`. Do not skip back to where the error occurred — run the full chain to confirm no additional missing packages exist.
5. **If `provision_ui_dependency` itself fails**: Escalate to the Director with the exact error output. Do not attempt manual `npm install` via bash — this bypasses the Zero-Trust CLI injection boundary.

### Why "Push Through" is Forbidden

When a module is missing, Vite's bundler emits cascading synthetic errors across every file that transitively imports from the broken module. These errors look like TypeScript type errors or Vitest assertion failures but are not — they are environment failures. Pushing through produces hallucinated patches (fixing code that is actually correct) and buries the real root cause. The only correct action is to fix the environment first.
