---
description: The official protocol for validating, auditing, and promoting `.staging/` codebase mutations back into the root workspace.
---

# Staging Promotion Protocol

**Purpose**: Formalizes the handoff and escalation matrix between the QA Engineer, Architect, and CLI Director during the final phase of codebase integrations to prevent recursion faults.

## Workflow Execution Steps

1. **Pre-Flight Testing (QA Engineer)**: Execute the full validation suite against `.staging/` code:
   - **Backend mutations**: Run `pytest tests/` via `execute_tdaid_test`. 
   - **Frontend mutations**: Run the full `/ui-qa-audit` workflow (TypeScript → Vitest → ESLint → visual screenshot). 
   - **CRITICAL**: Failing tests must be reported back to the Executor's iterative looping trace. Passing tests (`[QA PASSED]`) natively unlock the Executor to conclude its loop and subsequently pass the root line downward to the Auditor.

## Phase 3: The Native Pipeline Transition

3. **Staging Vetting (QA Engineer)**: If tests passed and the QA report looks structurally sound, the QA Engineer cleanly concludes (`[QA PASSED]`), returning the native execution state exclusively back to the Executor. The Executor issues `[EXECUTION COMPLETE]` to yield the sequence over to the Auditor.

4. **Holistic Audit (Auditor)**: The Lead Auditor reads the `.staging/` airspace AST structures. They run explicit FinOps anti-pattern queries and Zero-Trust credential sweeps. The Auditor independently verifies `.staging/.qa_signature` exists and the HMAC token is valid before calling `promote_staging_area`.

5. **Success Path (Auditor)**: If no blast-radius violations or architectural decay are identified, the Auditor leverages its exclusive access to `promote_staging_area` to natively merge the changes back into the root workspace. Following the deployment, the Auditor formally outputs `[AUDIT PASSED]`. **CRITICAL TDAID CONSTRAINT**: The promotion action permanently purges the `.staging/` sandbox.

6. **Denial Path (Auditor) & In-Situ Patching**: If errors are surfaced in audits (e.g., complexity constraints) or if `.staging/.qa_signature` is missing, the Auditor provides strict technical feedback (`[AUDIT FAILED]`). **CRITICAL**: The Auditor does NOT execute `teardown_staging_area`. The `.staging/` airspace is explicitly left intact.
7. **The Macro-Loop (CLI Director)**: The CLI Director actively traps the `[AUDIT FAILED]` trace and recursively loops an updated directive back into the Development Sequence. This permits the Executor to structurally patch its logic natively *in-situ* without constantly losing previous functional momentum. (Systemic Hallucination or Paradox escalations are still routed to the Human).
