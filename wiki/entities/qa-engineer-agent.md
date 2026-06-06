---
title: "QA Engineer Agent"
date: 2026-06-02
category: entity
tags:
  - agent
  - testing
  - tdaid
  - qa
  - playwright
sources:
  - "[[docs/decisions/2026-04-23_Spec-Driven_TDD_implementation_plan.md]]"
  - "[[docs/retrospectives/2026-04-23_kernel_graft_and_tdaid_stabilization.md]]"
  - "[[docs/retrospectives/2026-04-26_adk_2_0_iterative_refinement_migration.md]]"
last_ingested: 2026-06-02
---

# QA Engineer Agent

The QA Engineer is the adversarial test gate within the [[agentic-os]] swarm. Under the Spec-Driven TDD model, it authors test specifications, executes them via `execute_tdaid_test`, and gates code promotion through cryptographic `.qa_signature` HMAC verification.

## Architecture

The QA Engineer is a sequential sibling of the [[executor-agent]] within the `executor_loop`. Under the ADK 2.0 Iterative Refinement Pattern, the framework automatically sequences: Executor → QA → loop evaluation. The QA Engineer does **not** call `transfer_to_agent`; instead, it emits textual signals that the [[zero-trust-interceptors]] parse.

### Tool Bindings
- `execute_tdaid_test` — Runs Pytest against `.staging/` code
- `measure_cyclomatic_complexity` — Measures McCabe complexity
- `write_workspace_file` — Writes test files into `.staging/tests/`
- `transfer_to_development_workflow` — Writes the cryptographic `.qa_signature` HMAC

### Textual Signals
- `[QA REJECTED]` — Forces loop continuation; the Executor receives the traceback and structural hints
- `[QA PASSED]` — Terminates the `executor_loop` and promotes to the [[zero-trust-auditor]]

## Spec-Driven TDD

Under the Spec-Driven model ([docs/decisions/2026-04-23_Spec-Driven_TDD_implementation_plan.md](../docs/decisions/2026-04-23_Spec-Driven_TDD_implementation_plan.md)), the QA Engineer authors all test payloads first. This reversal ensures the Red Baseline phase is always satisfied — the test must crash before any implementation exists.

## Sandbox Confinement

All QA file generation is trapped within `.staging/tests/` using the same sandbox mapping rules applied to the Executor. The QA Engineer cannot bridge into the root host OS.

## Anti-Pattern Knowledge

The QA Engineer has access to the [[anti-pattern-knowledge-graph]] via pre-loaded static instructions. When encountering generic network errors (e.g., `ERR_CONNECTION_REFUSED`), it queries known anti-patterns before mutating test code.

## See Also

- [[executor-agent]] — The code mutation engine it gates
- [[tdaid-methodology]] — The governing Red-Green protocol
- [[staging-airlock]] — The sandboxed environment where tests run
- [[zero-trust-auditor]] — The next gate after QA approval
