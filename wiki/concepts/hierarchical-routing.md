---
title: "Hierarchical Routing"
date: 2026-06-02
category: concept
tags:
  - architecture
  - adk
  - sequential-agent
  - routing
sources:
  - "[[docs/retrospectives/2026-04-22_hierarchical_routing_pivot.md]]"
  - "[[docs/retrospectives/2026-04-26_adk_2_0_iterative_refinement_migration.md]]"
last_ingested: 2026-06-02
---

# Hierarchical Routing

Hierarchical Routing is the architectural pattern that replaced the original "Round-Table" `LoopAgent` design in the [[agentic-os]], using ADK's native `SequentialAgent` and `LoopAgent` primitives to create a directed execution tree.

## Evolution

### Era 2: Round-Table (Failed)
All agents shared a single `LoopAgent`, communicating via conversational context. This caused the [[token-tax]] — exponential context bloat from recursive JSON trace appending.

### Era 3: Hybrid Executor (Intermediate)
The QA Engineer was fused into the Executor's prompt to reduce node-to-node chatter. Fast but sacrificed the philosophical boundary of TDD isolation.

### Era 4: SequentialAgent Tree (Stable)
The pivot to ADK's native patterns. The Architect was formally decommissioned during this era ([iterative macro-looping retrospective](../docs/retrospectives/2026-04-23_iterative_macro_looping.md)), leaving a three-agent swarm:
```python
# Inner loop: Executor ↔ QA iteration
executor_loop = LoopAgent(max_iterations=15, sub_agents=[executor_agent, qa_agent])

# Sequential workflow: development cascade
development_workflow = SequentialAgent(sub_agents=[executor_loop])

# Outer loop: Director macro-retry
director_loop = LoopAgent(max_iterations=5, sub_agents=[development_workflow, auditor_agent])
```

### Era 5 (ADK 2.0): Iterative Refinement Pattern
Under ADK 2.0, `transfer_to_agent()` calls were fully purged. Agents conclude textually; the framework automatically sequences execution. Control flows are entirely organic via textual signals parsed by the [[zero-trust-interceptors]].

## Key Properties

- **Explicit Sub-Routing**: ADK natively supports `transfer_to_` graph mappings based on parent-child `sub_agent` relationships
- **Context Severance**: Each agent boundary is a serialization point — agents communicate via architectural payloads (handoff ledgers, textual signals), not continuous chat
- **Scope-Limited Termination**: Only the specific loop that matches the termination signal (`executor_loop`, `director_loop`) exits; parent loops are protected

## See Also

- [[token-tax]] — The problem hierarchical routing solved
- [[tool-parallelism-bottleneck]] — The residual cost of agent boundaries
- [[zero-trust-interceptors]] — The signal routing infrastructure
- [[director-agent]] — The outer macro-loop orchestrator
