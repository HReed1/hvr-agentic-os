---
description: A workflow for the Architect to passively monitor artifacts/executor_handoff.json and act as an adversarial QA engineer evaluating Executor Pytests.
---

# TDAID Audit Workflow

**Purpose**: Eliminates the QA cognitive load on the Director by mandating the Architect to read the Executor's locally generated TDAID JSON schemas from `artifacts/executor_handoff.json` and guarantee their validity before the Director issues `[TDAID QA: GREEN]`.

## Workflow Execution Steps

1. **Telemetry Ingestion**: Read the exact JSON payload dumped into `artifacts/executor_handoff.json`, ensuring you ingest the Executor's local diff buffers and Red/Green assertions. If the JSON does not exist: Halt and confirm with the Director to ensure The Executor delivered their payload.
2. **Adversarial Analysis**: Determine if the Executor's AST parsing (e.g., regex, AST libraries, or CLI dry-runs) is physically capable of evaluating the target Nextflow bounds. Specifically hunt for brittle "bunk string matching" that ignores complex Groovy `.map` closures.
3. **Approval Recommendation**: If the test is structurally sound, notify the Director: "Adversarial QA complete. The Pytest matrix is sound. Proceed to `[TDAID QA: GREEN]`."
4. **Denial Strategy**: If the test logic uses weak bracket-counting or hallucinates syntax, issue a strict architectural critique. Deny approval until the Executor refactors and passes a robust Red/Green loop.