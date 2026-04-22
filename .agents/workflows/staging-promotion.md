---
description: The official protocol for validating, auditing, and promoting `.staging/` codebase mutations back into the root workspace.
---

# Staging Promotion Protocol

**Purpose**: Formalizes the handoff and escalation matrix between the QA Engineer, Architect, and CLI Director during the final phase of codebase integrations to prevent recursion faults.

## Workflow Execution Steps

1. **Pre-Flight Testing (QA Engineer)**: Execute the full validation suite against `.staging/` code:
   - **Backend mutations**: Run `pytest tests/` via `execute_tdaid_test`. 
   - **Frontend mutations**: Run the full `/ui-qa-audit` workflow (TypeScript → Vitest → ESLint → visual screenshot). 
   - **CRITICAL**: Failing tests must be reported back to the Executor. Passing tests cleanly transition state natively up the workflow tree to the Auditor.

## Phase 3: The Native Pipeline Transition

3. **Staging Vetting (QA Engineer)**: If tests passed and the QA report looks architecturally sound, the QA Engineer cleanly concludes, returning the native execution state back to the Director to yield the root execution line to the Auditor.

4. **Holistic Audit (Auditor)**: The Lead Auditor reads the `.staging/` airspace AST structures. They run explicit FinOps anti-pattern queries and Zero-Trust credential sweeps. The Auditor independently verifies `.staging/.qa_signature` exists and the HMAC token is valid before calling `promote_staging_area`.

5. **Success Path (Auditor)**: If no blast-radius violations or architectural decay are identified, the Auditor leverages its exclusive access to `promote_staging_area` to natively merge the changes back into the root workspace. Following the deployment, the Auditor formally outputs `[AUDIT PASSED]`. **CRITICAL TDAID CONSTRAINT**: The promotion action permanently purges the `.staging/` sandbox.

6. **Denial Path (Auditor)**: If errors are surfaced in tests or audits (or if `.staging/.qa_signature` is missing/invalid), the Auditor immediately executes `teardown_staging_area` and provides strict technical feedback (`[AUDIT FAILED]`). The CLI Director reads the rejection and drafts a patch matrix for the Architect to iterate the Executor on.

7. **Systemic Resolution (CLI Director)**: Investigate hallucination loops. If Agent constraints, system prompts, skills, or directives require adjustment, the CLI Director MUST seek explicit Human User approval via the chat interface first.
