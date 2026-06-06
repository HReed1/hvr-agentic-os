---
title: "hvr-agentic-os"
date: 2026-06-02
category: entity
tags:
  - core
  - operating-system
  - multi-agent
  - adk
sources:
  - "[[docs/retrospectives/2026-04-23_hvr_agentic_os_meta_retrospective.md]]"
  - "[[docs/retrospectives/2026-04-23_agentic_os_drift_analysis.md]]"
last_ingested: 2026-06-02
---

# hvr-agentic-os

The `hvr-agentic-os` is a Zero-Trust Multi-Agent Operating System built on Google ADK (Agent Development Kit). It evolved from an aggressive monkey-patch of the ADK framework into a fully governed, hierarchical swarm architecture capable of executing automated coding workflows with cryptographic verification at every stage.

## Origin

The OS was born from the `google-adk` foundation to serve enterprise bioinformatics environments. Standard LLM routing arrays were inadequate for production clinical genomics workspaces, necessitating crash immunity, PHI redaction, and deterministic telemetry. The system was initially extracted from the sister repository `ngs-variant-validator`, which focuses on domain-specific bioinformatics capabilities while `hvr-agentic-os` serves as the hardened, mathematically constrained engine.

## Architectural Eras

The project evolved through five major eras:

1. **Era 1 — Framework Forge**: Monkey-patching ADK for crash immunity, PHI redaction (`dlp_proxy.py`), and telemetry extraction.
2. **Era 2 — Zero-Trust Stabilization**: Instituting the [[staging-airlock]], kernel throttling via `fcntl` locks, and resolving the memory paradox.
3. **Era 3 — Hierarchical Pivot**: Abandoning the "Round-Table" `LoopAgent` in favor of `SequentialAgent` trees to escape the [[token-tax]].
4. **Era 4 — TDAID Hardening**: Enforcing [[tdaid-methodology]] Red-Green baselines with chronological constraints.
5. **Era 5 — Context Caching & Head-to-Head**: Implementing [[context-caching]] for 56% token reduction, and the definitive [[solo-vs-swarm-benchmarks]] proving architectural trade-offs.

## Core Components

- **`agent_app/`** — The Python package containing agents, prompts, tools, and zero-trust interceptors.
- **`.agents/`** — Rules, workflows, skills, and memory ledgers governing the swarm.
- **`.staging/`** — The sandboxed airlock where all agent-generated code executes before promotion.
- **`tests/adk_evals/`** — The evaluation matrix driving automated benchmarks.
- **`bin/`** — Bash orchestration scripts for benchmarking, evaluation, and CI/CD.

## Sister Repository

The `ngs-variant-validator` repository contains the enterprise domain layer (bioinformatics, FinOps, infrastructure skills), while `hvr-agentic-os` provides the hardened orchestration kernel. A formal drift analysis ([docs/retrospectives/2026-04-23_agentic_os_drift_analysis.md](../docs/retrospectives/2026-04-23_agentic_os_drift_analysis.md)) documents the divergence between these two codebases.

## See Also

- [[director-agent]] — The top-level orchestration node
- [[executor-agent]] — The code mutation engine
- [[qa-engineer-agent]] — The adversarial test gate
- [[zero-trust-auditor]] — The final promotion authority
- [[staging-airlock]] — The sandbox execution environment
