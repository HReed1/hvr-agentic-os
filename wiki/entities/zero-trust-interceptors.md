---
title: "Zero-Trust Interceptors"
date: 2026-06-02
category: entity
tags:
  - security
  - zero-trust
  - signal-routing
  - loop-termination
sources:
  - "[[docs/retrospectives/2026-04-24_era5_evaluation_integrity_restoration.md]]"
  - "[[docs/retrospectives/2026-04-23_orchestration_stabilization_retrospective.md]]"
  - "[[docs/retrospectives/2026-04-26_adk_2_0_iterative_refinement_migration.md]]"
last_ingested: 2026-06-02
---

# Zero-Trust Interceptors

The `agent_app/zero_trust.py` module is the security spine of the [[agentic-os]]. It monkeypatches ADK's runtime to intercept LLM outputs, enforce signal routing, manage loop termination, and prevent hallucination cascades.

## Core Functions

### `patched_llm_run()`
Globally intercepts all Gemini inference requests, scrubbing the request matrices via the [[dlp-proxy]] before they enter the LLM context window. Ensures universal PHI blindness across the entire swarm.

### `patched_loop_run()`
Intercepts agent loop execution to handle textual signal routing:

| Signal | Terminates | Purpose |
|--------|-----------|---------|
| `[EXECUTION COMPLETE]` | `executor_loop`, `solo_loop` | Legacy clean exit |
| `[QA PASSED]` | `executor_loop`, `solo_loop` | Clean exit after QA approval |
| `[QA REJECTED]` | — | Loop continuation; Executor receives traceback |
| `[AUDIT PASSED]` | `director_loop`, `cicd_director_loop` | Clean exit after Auditor approval |
| `[AUDIT FAILED]` | — | Macro-loop retry via Director |

### Scope-Limited Termination
A critical constraint ensures only localized engines terminate their own loops:
```python
if getattr(self, 'name', '') in ('executor_loop', 'solo_loop'):
```
This strict object reflection prevents a child loop's exit signal from catastrophically killing the parent Director loop.

## Historical Fixes

- **Event Bubbling Recovery** ([orchestration stabilization](../docs/retrospectives/2026-04-23_orchestration_stabilization_retrospective.md)): `[AUDIT FAILED]` no longer kills the master process but bubbles feedback to the Director.
- **NoneType Evaluation Blindspot** ([head-to-head benchmarks](../docs/retrospectives/2026-04-21_head_to_head_benchmarks.md)): Coerces `None` inferences to empty arrays to prevent cascading crashes.
- **Aclosing Wrappers**: Aggressive pruning of crashed MCP tooling ports via `Aclosing` interceptors.

## See Also

- [[dlp-proxy]] — The PHI redaction layer invoked by `patched_llm_run`
- [[director-agent]] — The macro-loop that retries on `[AUDIT FAILED]`
- [[executor-agent]] — The inner loop terminated by `[QA PASSED]`
