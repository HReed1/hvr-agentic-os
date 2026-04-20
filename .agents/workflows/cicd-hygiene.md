---
description: Natively evaluates the global Pytest suite to generate mass tracebacks for systemic CI/CD remediation.
---

# CI/CD Hygiene Workflow

**Purpose:** Used by the CI/CD Hygiene Auditor to systematically diagnose and incrementally remediate broken testing suites (obsolescence removal or architectural syntax updating).

## Workflow Execution Steps

1. **Global Pipeline Tracing**: Use the `run_pipeline_diagnostics` tool natively to run the entire backend test suite. This tool is configured explicitly to bypass local environmental docker failures and strictly returns raw Python testing traces.
2. **Atomic Triage**: Parse the massive traceback payload. Determine whether the failures are isolated (e.g., bad syntax in a single router test) or systemic (e.g., synchronous testing databases colliding with async routing).
3. **Paced Delegation**: You MUST NOT handoff more than one broken module (e.g., `tests/test_api_routers_samples.py`) to the `@executor` per iteration. Handing off multiple broken modules simultaneously risks overwhelming the Executor and triggering endless syntax loops.
4. **Executor Handoff**: Synthesize a targeted payload directing the `@executor` to fix the specific testing file using standard read/write workspace tools.
5. **QA Assurance Check**: Wait for the Executor and QA Engineer to successfully resolve the atomic testing branch and invoke the `mark_qa_passed` tool back to you.
6. **Re-Auditing**: Re-run the `run_pipeline_diagnostics` tool. If failures persist, route the next broken module to the Executor.
7. **Pipeline Stabilization**: When `run_pipeline_diagnostics` explicitly yields exactly 0 failing modules (or merely exits cleanly), you MUST immediately output `[CI/CD PIPELINE STABILIZED]` to tear down your loop and return global control back to the IDE Director.
