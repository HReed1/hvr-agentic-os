---
title: "Director Agent"
date: 2026-06-02
category: entity
tags:
  - agent
  - orchestration
  - routing
  - macro-loop
sources:
  - "[[docs/retrospectives/2026-04-23_orchestration_stabilization_retrospective.md]]"
  - "[[docs/retrospectives/2026-04-23_iterative_macro_looping.md]]"
  - "[[docs/retrospectives/2026-04-24_context_caching_optimization_results.md]]"
last_ingested: 2026-06-02
---

# Director Agent

The Director is the top-level orchestration node in the [[agentic-os]] swarm hierarchy. It receives task directives from the human operator, scopes engineering boundaries, and routes execution through the `development_workflow` pipeline (see [[hierarchical-routing]]).

## Architecture

The Director operates inside a `LoopAgent` (`director_loop`, max 5 iterations) that provides macro-level retry logic. When the [[zero-trust-auditor]] rejects a payload via `[AUDIT FAILED]`, the Director intercepts the semantic feedback, wraps it into a fresh prompt directive, and re-routes execution back through the `development_workflow` for remediation.

## Key Behaviors

- **Macro-Loop Resurrection** ([docs/retrospectives/2026-04-23_orchestration_stabilization_retrospective.md](../docs/retrospectives/2026-04-23_orchestration_stabilization_retrospective.md)): Refactored to catch `[AUDIT FAILED]` signals and retry rather than hard-crashing.
- **Pre-Loaded Rules**: All `.agents/rules/*.md` files are injected into the Director's `static_instruction` at import time, eliminating 3–4 boot-read inferences per run.
- **Skill Delegation**: Routes `@skill` constraints to the appropriate sub-agent (primarily the [[qa-engineer-agent]] under the [[tdaid-methodology]] spec-driven model).

## Loop Termination

The Director exits cleanly when it receives `[AUDIT PASSED]` from the Auditor. The `zero_trust.py` interceptor handles this via the `patched_loop_run` function, terminating `director_loop` or `cicd_director_loop` specifically.

## See Also

- [[executor-agent]] — The code mutation engine under the Director
- [[zero-trust-auditor]] — The final gate before code promotion
- [[context-caching]] — Optimization that eliminated Director boot-read overhead
