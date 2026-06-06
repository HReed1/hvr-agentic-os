---
title: "Ephemeral Memory Handoff"
date: 2026-06-02
category: concept
tags:
  - memory
  - state-management
  - handoff
  - executor
sources:
  - "[[docs/retrospectives/2026-04-20_zero_trust_stabilization_and_telemetry.md]]"
  - "[[docs/retrospectives/2026-04-22_hierarchical_swarm_triumph.md]]"
  - "[[docs/retrospectives/2026-04-23_orchestration_stabilization_retrospective.md]]"
last_ingested: 2026-06-02
---

# Ephemeral Memory Handoff

The Ephemeral Memory Handoff is the mechanism by which the [[executor-agent]] persists architectural lessons and successful patterns across sessions, bridging the [[amnesia-sweep]] gap.

## Architecture

The Executor writes novel insights to `.staging/.agents/memory/executor_handoff.md` during sandbox execution. This ledger is loaded at runtime via the `load_handoff_ledger()` function and injected into the Executor's per-turn instruction via ADK's `InstructionProvider` pattern.

### What Gets Written
- Successful architectural implementations (e.g., dictionary dispatch routing)
- Testing infrastructure constraints (e.g., ASGI polling requirements)
- Safe `write_to_file` targeting restrictions in sandboxes
- Async `Depends()` decoupling validation patterns

### What Gets Filtered
The Executor is encouraged to filter out redundant operations (standard Pytest generation) to prevent spamming the Director's memory ledger with duplicate context.

## Critical Constraints

### Timing
The Executor is strictly forbidden from appending to `executor_handoff.md` **after** the [[qa-engineer-agent]] has passed tests. Post-QA sandbox mutations invalidate the HMAC `.qa_signature`, causing fatal [[zero-trust-auditor]] deployment failures.

### Location
All handoff writes must target `.staging/.agents/memory/executor_handoff.md` (inside the sandbox boundary), never the root workspace. This was fixed after the "Memory Paradox" where an `.agents/rules` matrix incorrectly forced writes to a phantom `artifacts/` directory.

### The Handoff Ledger Limitation
The ledger accelerates *reasoning* but cannot accelerate *topology*. Even perfect first-pass code still requires the irreducible agent-boundary serialization points — see [[tool-parallelism-bottleneck]].

## See Also

- [[executor-agent]] — The agent that writes and reads the handoff ledger
- [[amnesia-sweep]] — The destruction protocol the ledger survives
- [[context-caching]] — Complementary optimization via `static_instruction`
- [[tool-parallelism-bottleneck]] — Why the ledger can't fix topological overhead
