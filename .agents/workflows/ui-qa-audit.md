---
description: The official QA protocol for validating and asserting React UI structural changes autonomously within the `.staging/` environment.
---

# UI QA Audit Workflow

**Description**: The official protocol for validating and asserting React UI structural changes autonomously within the `.staging/` environment or the local Vite DOM.
**Owner**: QA Engineer exclusively. The Executor stages code and then yields. All steps below are QA Engineer actions.
**Linked Skills**: `@vite-reactor-suite`

This workflow guarantees the Swarm acts as an adversarial QA engineer evaluating Executor UI modifications, establishing regression-free Zero-Trust architecture. Before authorizing the Executor to merge frontend changes into the `ngs-variant-ui` core block, the Director must invoke this protocol.

## Step 1: Enforce UI Governance Rules
- Review the staged changes against `.agents/rules/frontend-react-governance.md`.
- Verify that `@tanstack/react-query` has been used for API state management. Raw `useEffect` loops for async data fetching are prohibited.
- Verify no TailwindCSS classes have been introduced (TailwindCSS has been removed from this project; native Vanilla CSS Glassmorphism is mandated).
- Check that all TypeScript interfaces in `src/types/` remain in sync with backend Pydantic models.

## Step 2: Trigger the Vite Reactor Suite
Enable the test sandbox first: call `toggle_react_eval_mode(enable=True)` to set `VITE_MOCK_AUTH=true`.

### A) Dependency Pre-Check
Before running any validation, scan the staged import declarations for packages that may not be installed in `.staging/ngs-variant-ui/node_modules/`. If any package is unrecognized, call `provision_ui_dependency` now — before compilation. **Do not wait for a failure to discover missing dependencies.**

### B) Native Type Interrogation
1. Call `evaluate_typescript_diagnostics`.
2. If compilation fails with "Failed to resolve import" or "Cannot find module" → call `provision_ui_dependency` immediately, then restart from Step 2A.
3. If compilation fails with a genuine TypeScript type error → hand control back to the Executor with the exact error output. Do not attempt inline code fixes.

### C) VDOM Logic Validation
1. Call `run_vitest_evaluation` targeting the modified files via pattern matching.
2. If tests fail to run due to missing setup mocks (e.g., `ResizeObserver`, `window.matchMedia`) → instruct the Executor to add the mock to `vitest.setup.ts`. Do not push through test infrastructure failures.
3. If tests fail due to assertion failures → hand control back to the Executor with the exact failure output.

### D) ESLint Glassmorphism Audit
1. Call `audit_eslint_glassmorphism` targeting the staged files.
2. All ESLint errors MUST be resolved before proceeding. Common violations: `no-explicit-any`, `prefer-const`, unused imports. Hand control to the Executor for each violation with the exact file and line number.
3. Warnings may be noted but do not block promotion.

### E) Visual Smoke Test
1. Call `capture_ui_screenshot` for the affected routes to verify no layout regressions.
2. Use multimodal inspection to confirm glassmorphism styling is intact, z-index layering is correct, and no blank panels are visible.

## Step 3: Close the Auth Bypass
Call `toggle_react_eval_mode(enable=False)` to restore Zero-Trust policies. **This must happen regardless of pass/fail outcome.**

## Step 4: Cryptographic Gate — `mark_qa_passed` (MANDATORY)
After all of Steps 2B, 2C, 2D, and 2E pass cleanly:

1. Call `mark_qa_passed`. This writes the HMAC token to `.staging/.qa_signature`.
2. Confirm the tool acknowledges the write.
3. Report `[QA PASSED]` to the Architect.

**Without this step, `promote_staging_area` is physically blocked.** A `[SUCCESS]` string in the chat transcript is not a cryptographic token. The Auditor reads the physical file — if it doesn't exist, the staging promotion is rejected. This is the most common source of session failures. Do not skip it.
