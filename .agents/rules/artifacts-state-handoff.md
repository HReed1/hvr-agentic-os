---
trigger: always_on
description: Enforces the use of exact physical JSON/YAML payloads for Swarm analytical state transitions.
---

# The Artifacts State Handoff Rule

Whenever the Executor or Architect is active within the sandbox, they MUST format their analytical payloads, Git `.diff` buffers, and final Pytest outcomes into a strict JSON/YAML payload.

This payload MUST be written directly to `artifacts/architect_handoff.json` (if Architect) or `artifacts/executor_handoff.json` (if Executor). The Swarm Director relies on these physical files exclusively to evaluate State Machine routing boundaries.
