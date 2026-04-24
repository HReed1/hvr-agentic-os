# Spec-Driven TDD: QA Engineer Reverse Routing

This plan details the structural shift to make the **QA Engineer** responsible for authoring all test specifications. By forcing the QA Engineer to write the Red Baseline tests *first*, we completely resolve the "One-Shot" bug caused by the Executor generating functional code prematurely, all without introducing the token overhead of a third "Test Engineer" agent.

## User Review Required
> [!IMPORTANT]
> Promoting the QA Engineer to "Spec Author" means we must actively grant the QA Engineer file mutation tools (`write_workspace_file`). To address security and Zero-Trust isolation, we must strictly ensure QA file generation bounds are trapped physically within `.staging/tests/` using the precise sandbox mapping rules currently applied to the Executor.

## Proposed Changes

We will reverse the hierarchy, ensuring the Director passes directives to QA first, effectively formalizing Spec-Driven Test-Driven Development (TDD).

### Agentic Prompts Core

#### [MODIFY] [prompts.py](file:///Users/harrisonreed/Projects/hvr-agentic-os/agent_app/prompts.py)
*   **[MODIFY] `qa_instruction`**: 
    1.  **Test Authoring:** Assign the QA Engineer full responsibility for authoring all `tests/` payloads. It must execute the tests natively and use the subsequent `[QA REJECTED]` to transfer the traceback bounds down to the Executor.
    2.  **Sandbox Confinement (Zero-Trust):** Inject the exact Sandbox guardrails into the QA prompt: `"All your tooling invocations like write_workspace_file or execute_transient_docker_sandbox are physically trapped inside the .staging/ airlock. You MUST use normal relative paths; the framework will map them automatically."` This ensures its file drafting capabilities cannot bridge into the root host OS.
    3.  **Playwright Skill Integration:** Explicitly prompt the QA Engineer to read and apply `@skill:playwright-engineer`. It must natively understand how to configure contexts to extract volumetric Playwright trace `.zip` archives into `.staging/artifacts` as detailed in the skill markdown.
    4.  **Differentiated Spec Routing:** Instruct QA to dynamically distinguish between standard Pytest (Backend API) and Playwright E2E (Frontend GUI) testing bounds based on the Director's intent, applying the appropriate fixtures (e.g., `subprocess.Popen` with purely `--host localhost`).
*   **[MODIFY] `executor_instruction`**: Explicitly restrict the Executor from interacting with the testing framework. Its sole responsibility is to evaluate the failing traceback injected by the QA Engineer and author the structural `api/` or DOM code needed to pass the tests.
*   **[MODIFY] `director_instruction`**: 
    1.  **Routing Change:** Update the internal semantic routing hierarchy so new workflow requests target the QA Engineer as the beginning of the Spec-Driven cascade natively.
    2.  **Skill Delegation:** Ensure the ``SEMANTIC DELEGATION`` clause instructs the Director to pass the `@skill` constraints directly to the QA Engineer (so QA knows what tests to write) rather than exclusively the Executor.

### Zero-Trust Tooling Bindings

#### [MODIFY] [agents.py](file:///Users/harrisonreed/Projects/hvr-agentic-os/agent_app/agents.py) (and `tools.py` bounds if applicable)
*   **[MODIFY] Tool Registry:** Attach `write_workspace_file` and relevant file manipulation tools to the `QA Engineer` configuration block to allow native payload creation.

## Verification Plan

### Automated Tests
*   Update the `.staging/tests/test_tdaid_routing.py` payload to:
    1.  Assert the QA Engineer's instructions now contain phrases delegating Test Generation specifically.
    2.  Assert `@skill:playwright-engineer` is actively mentioned as a required integration bound within the QA prompt.
    3.  Assert the Sandbox Confinement clause explicitly exists within the QA Engineer's guardrails.
    4.  Assert the Executor is explicitly removed from testing execution logic.
*   Upon approval, the modified routing logic will undergo a full test-battery loop in the execution sandbox.
