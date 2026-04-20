---
description: The official protocol for validating, auditing, and promoting `.staging/` codebase mutations back into the root workspace.
---

# Staging Promotion Protocol

**Purpose**: Formalizes the handoff and escalation matrix between the QA Engineer, Architect, and CLI Director during the final phase of codebase integrations to prevent recursion faults.

## Workflow Execution Steps

1. **Pre-Flight Testing (QA Engineer)**: Execute the full validation suite against `.staging/` code:
   - **Backend mutations**: Run `pytest tests/` via `execute_tdaid_test`. Then call `mark_qa_passed` to write `.staging/.qa_signature`.
   - **Frontend mutations**: Run the full `/ui-qa-audit` workflow (TypeScript → Vitest → ESLint → visual screenshot). Then call `mark_qa_passed` to write `.staging/.qa_signature`.
   - **CRITICAL**: `mark_qa_passed` is not optional. Without `.staging/.qa_signature`, `promote_staging_area` is hard-blocked by the HMAC crypto gate regardless of what the QA Engineer reports verbally.

2. **Handoff (QA Engineer)**: Report `[QA PASSED]` alongside a semantic summary of the changes (files modified, test results, ESLint status) to the Architect.

3. **Staging Vetting (Architect)**: If tests passed and the QA report looks architecturally sound, the Architect verifies `.staging/.qa_signature` exists and yields the root execution line to the Auditor. (The Architect is explicitly forbidden from deploying code. The tool name is `mark_qa_passed` — there is no `approve_staging_qa` tool.)

4. **Holistic Audit (Auditor)**: The Lead Auditor reads the `.staging/` airspace AST structures. They run explicit FinOps anti-pattern queries and Zero-Trust credential sweeps. The Auditor independently verifies `.staging/.qa_signature` exists and the HMAC token is valid before calling `promote_staging_area`.

5. **Success Path (Auditor)**: If no blast-radius violations or architectural decay are identified, the Auditor leverages its exclusive access to `promote_staging_area` to natively merge the changes back into the root workspace. Following the deployment, the Auditor formally outputs `[AUDIT PASSED]`. **CRITICAL TDAID CONSTRAINT**: The promotion action permanently purges the `.staging/` sandbox.

6. **Denial Path (Auditor)**: If errors are surfaced in tests or audits (or if `.staging/.qa_signature` is missing/invalid), the Auditor immediately executes `teardown_staging_area` and provides strict technical feedback (`[AUDIT FAILED]`). The CLI Director reads the rejection and drafts a patch matrix for the Architect to iterate the Executor on.

7. **Systemic Resolution (CLI Director)**: Investigate hallucination loops. If Agent constraints, system prompts, skills, or directives require adjustment, the CLI Director MUST seek explicit Human User approval via the chat interface first.
