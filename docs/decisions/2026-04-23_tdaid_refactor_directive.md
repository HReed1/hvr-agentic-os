# TDAID Architecture Refactor & Decoupling Directive

**@director** (Antigravity IDE Agent)

## 1. Holistic Assessment
Our agentic swarm operates on a Zero-Trust Test-Driven AI Development (TDAID) methodology. However, deploying Gemini 3.1 Pro Preview introduced an emergent friction layer: the "one-shot" capability allows the logic branch to author the test payload (`test__.py`) and the corresponding functional framework (`api/`) concurrently in a single execution. While technically optimal, it bypasses the physical requirement of yielding a verifiable Red Baseline failure trace first.

## 2. Zero-Trust Action Bounds
**CRITICAL MANDATE: READ-ONLY RESEARCH.** 
You are strictly forbidden from mutating physical source code, executing sandbox teardowns, or modifying swarm bash automation loops in this session. 

Your sole responsibility is to survey the current Swarm topology and determine how we can logically or physically separate the Test Generator persona from the Functional Code Generator persona (or stages), maximizing verification confidence without triggering infinite escalation paradoxes.

## 3. Execution Steps
1. **Trace the Existing Paradigm**: Natively examine `agent_app/prompts.py` (specifically `executor` and `qa_engineer` logic) and the test execution bindings in `utils/ast_validation_mcp.py` to identify current workflow bottlenecks.
2. **Investigate Alternative Framework Roles**: Identify if existing workflow loops natively support sequential chunking. Would spinning up a dedicated `@test_engineer` agent prior to invoking the `executor` alleviate the friction, or should the Executor simply pause after writing tests and wait for QA feedback?
3. **Formulate the Engineering Plan**: Draft an internal architectural proposal detailing your recommended technical mapping to transition the repository away from concurrent test/code authoring.
4. **Handoff for Debate**: Synthesize your completed proposal directly into an `implementation_plan` Antigravity Artifact and immediately halt all code execution. The Human Operator will read the artifact and physically debate the logic with you.

---
**TDAID Injection Checkpoint:** *(Reference Rule)*
Create an offline isolated TDAID Python test asserting the required mutation (Red/Green schema) targeting your modifications. You are the author ONLY. You do NOT have the capability to execute tests. Do NOT hallucinate testing tools or bash runners. The QA Engineer will physically use `execute_tdaid_test` to validate your work after you handoff. Once you have written the `.staging` codebase, output [TASK COMPLETE].
