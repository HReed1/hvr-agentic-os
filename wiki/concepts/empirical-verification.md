---
title: "Empirical Verification"
date: 2026-06-02
category: concept
tags:
  - methodology
  - debugging
  - verification
  - diagnostics
sources:
  - "[[docs/retrospectives/2026-04-25_tool_parallelism_bottleneck_analysis.md]]"
  - "[[docs/retrospectives/2026-04-23_kernel_graft_and_tdaid_stabilization.md]]"
last_ingested: 2026-06-02
---

# Empirical Verification

Empirical Verification is a core methodological principle of the [[agentic-os]]: no architectural changes or code workarounds may be implemented based on symptom-matching or "Black Box" assumptions. The precise root mechanism of a failure must be identified and verified through direct inspection before any modification is applied.

## The Three Mandates

### 1. Physical Evidence First
Actively verify ground-truth state using native diagnostic tools — execute trace logs, inspect physical file states, query actual databases. Never rely on session memory.

### 2. Never Guess System Bounds
If a system constraint (firewall, sandbox, permission gate) is suspected of interfering, read and verify the structural constraints or exact source code governing that boundary. Provide verifiable proof.

### 3. Trace the Literal Data Pipeline
Do not assume what an external system "might" be doing. Trace literal data pipeline bounds and exact structural inputs/outputs to identify the precise point of failure.

## Origin Story

This principle was formalized after multiple incidents where the Swarm misdiagnosed infrastructure failures as application bugs:

- **The ASGI Latency Paradox**: Pytest swallowed `ERR_CONNECTION_REFUSED` errors from Uvicorn boot timing, causing the Swarm to endlessly rewrite correct backend code ([see anti-pattern](../docs/anti-patterns/asgi_playwright_latency.md))
- **The Tool Parallelism Discovery**: The initial hypothesis of "data contamination" in Solo benchmarks was disproven by forensic trace analysis of raw evaluation JSON, revealing legitimate tool parallelism as the actual mechanism ([docs/retrospectives/2026-04-25](../docs/retrospectives/2026-04-25_tool_parallelism_bottleneck_analysis.md))

## Application to Self-Healing (Era 4)

The Era 4 roadmap proposes Diagnostic MCP Wrappers that give the [[qa-engineer-agent]] read-only access to host-level observability (`tail_background_process`, `audit_network_sockets`) to empirically verify infrastructure state before diagnosing failures.

## See Also

- [[anti-pattern-knowledge-graph]] — The documented failure modes that inform empirical investigation
- [[tdaid-methodology]] — The testing protocol that demands provable failures
- [[evaluation-framework]] — Where empirical verification is most critical
