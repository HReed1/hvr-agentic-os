---
name: swarm-handoffs
description: Official rules of engagement for Agentic Swarm handoffs, Zero-Trust text signals, and ephemeral memory synchronization.
---

# Swarm Handoff Mechanics & Zero-Trust Protocol

The Agentic Swarm relies on a mixture of structural API calls (`transfer_to_agent`) and exact text-based interceptor signals (e.g., `[QA REJECTED]`) to manage control flow. **Failure to adhere to these mechanics will result in catastrophic loops or premature terminations.**

## The Golden Rule of Text Signals
The Zero-Trust Python backend uses regular expressions to intercept control signals in your text output. 
**You are strictly forbidden from writing or echoing any control signal (e.g., quoting a signal in your thoughts, instructions, or summaries) UNLESS you are explicitly issuing that signal to change the execution state.** If a Director or QA Engineer casually writes `[QA REJECTED]` in a directive or thought process, the system will immediately escalate and kill the evaluation.

## 1. Director ↔ Executor Handoffs
* **Mechanism**: `transfer_to_agent(agent_name="development_workflow")`
* **Director Role**: You are the orchestrator. You do not write code. When you have synthesized a directive, you MUST invoke `transfer_to_agent` to pass the bounds to the Executor.
* **Return Signal**: Control only returns to the Director when the Auditor issues `[AUDIT PASSED]` or `[AUDIT FAILED]`, or if the Zero-Trust framework forces an escalation.

## 2. Executor ↔ QA Engineer Handoffs (The TDAID Loop)
* **Mechanism (Executor -> QA)**: Native ADK 2.0 Loop Agent Iteration. The Executor and QA Engineer are siblings in a LoopAgent. The Executor simply concludes its text response, and control naturally flows to the QA Engineer. DO NOT use `transfer_to_agent` for this step.
* **Mechanism (QA -> Executor)**: Emitting `[QA REJECTED]` or `[QA PASSED]` text signals. `[QA REJECTED]` continues the LoopAgent execution sequence, forcing the loop to start over at the Executor. `[QA PASSED]` successfully terminates the loop and moves execution to the Auditor.
* **The Ephemeral Memory Ledger**: The Executor operates in stateless amnesia to save tokens. When passing control to the QA Engineer, the context is wiped. To survive this, the system relies on `.staging/.agents/memory/executor_handoff.md`.
    * **Executor**: Must read the ledger to regain context, and optionally append 1-2 sentences of structural progress before transferring to the QA Engineer.
    * **QA Engineer**: Must ALWAYS read the ledger before authoring a test to ensure it doesn't repeat historical testing paradoxes.

## 3. QA Engineer Signals
The QA Engineer exclusively dictates whether the code in `.staging/` is valid.
* **Rejection (`[QA REJECTED]`)**: 
  When a test fails, the QA Engineer MUST emit this exact format:
  ```
  [QA REJECTED]
  ASSERTION: <exact pytest assertion or traceback>
  ROOT CAUSE: <1 sentence explaining why>
  FIX HINT: <1 sentence telling the Executor what file/line to change>
  ```
  *This intercepts the loop and kicks the traceback back to the Executor.*
* **Pass (`[QA PASSED]`)**: 
  When a test organically returns Exit 0, the QA Engineer MUST emit `[QA PASSED]` on its own line and conclude its turn. *This terminates the `executor_loop` and bubbles control up to the Auditor.*

### The TDAID Red Baseline Exception (Expected Failures)
Under the Test-Driven AI Development (TDAID) methodology, **at least 1 test failure is expected per round**.
* **The Expected Failure**: The QA Engineer MUST write a "Red Baseline" test proving a new feature does not exist yet. When this test organically fails, the QA Engineer MUST emit `[QA REJECTED]` to pass the traceback to the Executor.
* **The Zero-Trust Interceptor Mechanic**: The underlying Python orchestration harness is designed to expect this. It tracks the exact text of your `[QA REJECTED]` payload (the `_last_rejection_signature`). 
* **The Threshold**: The system will ONLY trigger a fatal escalation if it intercepts the **exact same `[QA REJECTED]` signature twice in a row**. This implies the Executor failed to make material progress. If the signature changes (i.e. a new test fails, or the same test fails for a different reason), the harness resets the counter to 1 and allows the loop to organically continue. Do not be afraid to reject code; it is the engine of progress.

## 4. Auditor ↔ Director Handoffs
The Auditor acts as a read-only FinOps and Security gate.
* **Pass (`[AUDIT PASSED]`)**: Emitted when the staging code satisfies Zero-Trust, complexity bounds (McCabe <= 5), and has been successfully promoted via `promote_staging_area`. *This terminates the `development_workflow` and returns control to the Director.*
* **Fail (`[AUDIT FAILED]`)**: Emitted when code is too complex or violates security. *This kicks control back to the Director, who must then re-task the Executor to patch the staging area.*

## 5. Director ↔ Reporter Handoffs
* **System Complete**: When the Director receives `[AUDIT PASSED]`, it MUST invoke the `mark_system_complete` tool.
* **Reporting**: This triggers the Reporting Director to synthesize the full trace and output `[REPORT COMPLETE]`, officially terminating the autonomous Swarm.

---
**Summary**: Never hallucinate signals. Use `transfer_to_agent` only to push execution into sub-workflows (e.g. Director -> development_workflow). Use ADK 2.0 Loop iteration and `[QA REJECTED]/[PASSED]`, `[AUDIT FAILED]/[PASSED]` to organically route within and exit loops.
