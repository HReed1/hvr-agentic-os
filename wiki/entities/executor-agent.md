---
title: "Executor Agent"
date: 2026-06-02
category: entity
tags:
  - agent
  - code-generation
  - tdaid
  - executor
sources:
  - "[[docs/retrospectives/2026-04-23_kernel_graft_and_tdaid_stabilization.md]]"
  - "[[docs/retrospectives/2026-04-26_adk_2_0_iterative_refinement_migration.md]]"
  - "[[docs/decisions/2026-04-23_Spec-Driven_TDD_implementation_plan.md]]"
last_ingested: 2026-06-02
---

# Executor Agent

The Executor is the code mutation engine within the [[agentic-os]] swarm. It receives task directives (either from the [[director-agent]] or from QA rejection tracebacks), writes source code into the [[staging-airlock]], and iterates with the [[qa-engineer-agent]] until tests pass.

## Architecture

The Executor operates within an `executor_loop` (`LoopAgent`, max 15 iterations) alongside the [[qa-engineer-agent]] as sequential siblings. Under the ADK 2.0 Iterative Refinement Pattern, the framework automatically sequences execution: Executor → QA Engineer → loop evaluation.

### Tool Bindings
- `write_workspace_file` — Writes code into `.staging/`
- `read_workspace_file` — Reads the current sandbox state
- `list_workspace_directory` — Discovers sandbox file structure
- Does **not** possess `execute_tdaid_test` — that belongs exclusively to the [[qa-engineer-agent]]

## Key Constraints

### Chronological Mandate
The Executor is **forbidden** from writing functional code during its first execution pulse. It must immediately draft Grey Box Stubs and yield to the QA Engineer for Red Baseline testing. This was engineered to prevent the "one-shot" paradox where highly capable models (Gemini 3.1 Pro Preview) would generate tests and implementations simultaneously, bypassing the [[tdaid-methodology]] Red Baseline phase.

### Negative Deployment Constraints
Specific restrictions enforced during the initial drafting phase:
- Forbidden from writing `@app.get` decorators or functional implementations
- May only draft bare minimum stubs to prevent `ModuleNotFoundError`
- Must not mutate `executor_handoff.md` after QA has passed (to preserve HMAC signatures)

### Cyclomatic Complexity
All code must maintain a McCabe cyclomatic complexity score of ≤ 5 per function. The [[zero-trust-auditor]] physically measures this and rejects violations.

## Ephemeral Memory

The Executor writes architectural lessons and successful patterns to `.staging/.agents/memory/executor_handoff.md`. This ledger persists across the [[amnesia-sweep]] and accelerates future reasoning — though it cannot overcome the [[tool-parallelism-bottleneck]].

## See Also

- [[qa-engineer-agent]] — The adversarial test gate
- [[tdaid-methodology]] — The Red-Green testing protocol
- [[staging-airlock]] — The sandboxed execution environment
