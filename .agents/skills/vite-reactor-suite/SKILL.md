---
name: vite-reactor-suite
description: Provides strict programmatic UI validations for the QA Engineer via the Model Context Protocol. Use this to explicitly evaluate TypeScript configurations, run Vitest matrix logic, and block ESLint hallucinations before pushing React changes.
---

# Vite Reactor Suite

The UI ecosystem inside `ngs-variant-ui` leverages a strict Vite, React, and TypeScript configuration with native Vanilla CSS Glassmorphism (TailwindCSS has been removed — do not reference it). The ADK Swarm must use this MCP suite to deterministically ensure that autonomous code mutations do not generate invalid UI structural boundaries.

## When to use this skill
- When refactoring React functional components (`.tsx`).
- After declaring or modifying TypeScript interfaces and types (`.d.ts`, `.ts`).
- Before committing UI changes, to guarantee regression-free functionality.

## Who owns this skill

**This skill belongs exclusively to the QA Engineer.** The Executor does not call these tools. The Executor's role ends at staging the code mutation. The QA Engineer picks up from there and owns the full validation chain through `mark_qa_passed`.

## How to use it

As the QA Engineer, you possess direct structural access to the MCP validation tools under this server. You MUST prioritize utilizing these endpoints over executing raw bash `npm` commands, as these endpoints guarantee string-truncation rendering preventing Swarm buffer-overflow failures.

## CRITICAL: Missing Dependency Protocol

If **any** tool in this suite returns a `"Failed to resolve import"`, `"Cannot find module"`, `import-analysis` error, or any variant of a missing npm package error — **STOP immediately**. Do NOT push through it. Do NOT tell the Executor to run `npm install`. Execute the following recovery sequence before anything else:

1. Call `provision_ui_dependency` with the exact missing package name.
2. Confirm the tool returns success.
3. Restart the validation chain from `evaluate_typescript_diagnostics`.

Pushing through unresolved imports causes downstream Vitest failures that are misdiagnosed as code defects, wasting Executor cycles and producing hallucinated test patches.

### 1. `evaluate_typescript_diagnostics`
- **Mandate**: Execute this tool first. 
- **Purpose**: Before testing React logic, you must prove the component tree compiles. 
- **Action**: If this fails, read the JSON traceback, patch the TypeScript interface boundary directly, and repeat until clean. Note that you may need to update inherited API schemas if backend FastAPI logic was changed simultaneously.

### 2. `run_vitest_evaluation`
- **Mandate**: Execute this tool second.
- **Purpose**: Proves logical execution of the DOM boundaries natively in JSDOM via Vitest. 
- **Action**: Provide a `pattern` string argument (e.g. `RunQualityChart.test.tsx`) to isolate specific matrices. Fix test assertions before moving to styling.

### 3. `audit_eslint_glassmorphism`
- **Mandate**: Execute this tool third.
- **Purpose**: Enforces the `react-glassmorphism.md` and `frontend-react-governance.md` styling parameters natively.
- **Action**: Targets specific files. Prevents pushing messy DOM parameters or anti-patterns into production payloads.

### 4. `capture_ui_screenshot`
- **Mandate**: Execute this visual verification tool lastly, or whenever layout paradoxes occur.
- **Purpose**: Grants the Swarm the biological ability to dynamically see `.tsx` rendering via a Headless Playwright instance.
- **Action**: Pass the designated router path (e.g., `/architect`, `/finops`) to receive the physical screenshot context file. Use your native multi-modal inference to verify bounding boxes, z-index properties, and colors.
- **Critical Auth0 Bypass**: **Before executing this tool**, you MUST inject `VITE_MOCK_AUTH=true` into the file `ngs-variant-ui/.env.local` to instruct Node/Axios to drop the Auth0 JWKS interceptor and utilize the `X-Telemetry-Secret` payload natively! Failure to bypass this lock guarantees your screenshots will permanently depict the Auth0 MFA loop.

### 5. `toggle_react_eval_mode`
- **Mandate**: Execute this specifically to turn the `VITE_MOCK_AUTH` bypass ON or OFF physically.
- **Purpose**: Creates the sandbox environment enabling headless bots to see the DOM. Remember to supply `enable=False` at the end of testing to restore Zero-Trust policies locally.

### 6. `playwright_evaluate_interaction`
- **Mandate**: Use this specifically to test UI side-effects without the massive overhead of a Browser Subagent.
- **Purpose**: Programmatically clicks buttons or hovers over UI elements, dumping the post-interaction screen capture into `.staging/`. Use this to assert if FastAPI endpoints actually respond to active UI clicks.

### 7. `provision_ui_dependency`
- **Mandate**: **MANDATORY first response** to any "Failed to resolve import", "Cannot find module", or `import-analysis` error. Do not attempt any other action until this is called and confirmed successful.
- **Purpose**: Safely initiates an `npm install <package_name>` execution isolated directly within the `.staging/ngs-variant-ui/node_modules/` layer. Validates the payload safely preventing Zero-Trust CLI injections.
- **Action**: Pass the canonical package name (e.g., `react-toastify`) and confirm output success before attempting to rebuild or re-run tests. After success, restart the full validation chain from `evaluate_typescript_diagnostics` — do not skip back to where you were.

### 8. `mark_qa_passed`
- **Mandate**: Execute this immediately after `run_vitest_evaluation` returns `[SUCCESS]` AND `audit_eslint_glassmorphism` returns clean. This is the final step of every UI validation cycle.
- **Purpose**: Writes the HMAC cryptographic token to `.staging/.qa_signature`. Without this file, `promote_staging_area` is physically blocked — it reads and verifies the signature before merging. A `[SUCCESS]` string in chat is not a substitute.
- **Action**: Call `mark_qa_passed` with no arguments. Confirm the tool acknowledges the write. Then report `[QA PASSED]` to the Architect to trigger the staging promotion workflow.
