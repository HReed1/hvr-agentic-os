---
title: "Project Overview"
date: 2026-06-02
category: synthesis
tags:
  - wiki
  - overview
  - project-summary
sources:
  - "[[docs/retrospectives/2026-04-23_hvr_agentic_os_meta_retrospective.md]]"
  - "[[docs/retrospectives/2026-04-24_context_caching_optimization_results.md]]"
  - "[[docs/retrospectives/2026-04-24_era_5_head_to_head_conclusion.md]]"
  - "[[docs/retrospectives/2026-04-25_tool_parallelism_bottleneck_analysis.md]]"
  - "[[docs/retrospectives/2026-04-26_adk_2_0_iterative_refinement_migration.md]]"
last_ingested: 2026-06-02
---

# hvr-agentic-os — Living Overview

> Multi-agent orchestration operating system built on Google ADK 2.0, featuring hierarchical swarm architecture and zero-trust governance.

## What It Is

`hvr-agentic-os` is a Zero-Trust Multi-Agent Operating System that transforms Google's Agent Development Kit (ADK) into a production-grade autonomous coding platform. It enforces [[tdaid-methodology]] (Test-Driven AI Development) — a rigorous Red → Green → Refactor cycle with cryptographic verification gates at every stage.

The system evolved through five major architectural eras, starting as an aggressive monkey-patch of ADK for crash immunity and HIPAA-compliant PHI redaction, and maturing into a mathematically constrained orchestration kernel validated by empirical benchmarks.

## Architecture

The swarm executes in a [[hierarchical-routing]] tree:

```
director_loop (LoopAgent, max 5)
├── development_workflow (SequentialAgent)
│   └── executor_loop (LoopAgent, max 15)
│       ├── executor_agent (code mutation)
│       └── qa_agent (adversarial testing)
└── auditor_agent (promotion gate)
```

> [!NOTE]
> The Architect agent was formally decommissioned during Era 4 ([iterative macro-looping retrospective](../docs/retrospectives/2026-04-23_iterative_macro_looping.md)). Its read-only analytical role now exists only as the Antigravity IDE's `@architect` persona — an outer-layer orchestration entity, not an in-swarm agent.

All code mutation occurs inside the [[staging-airlock]] (`.staging/`). The [[zero-trust-interceptors]] in `zero_trust.py` monkeypatch ADK's runtime to enforce signal routing, loop termination, and PHI scrubbing via the [[dlp-proxy]].

## Key Agents

- **[[director-agent]]**: Scopes directives, routes execution, retries on `[AUDIT FAILED]`
- **[[executor-agent]]**: Writes code under chronological and complexity constraints
- **[[qa-engineer-agent]]**: Authors test specs, enforces Red Baselines, gates via HMAC
- **[[zero-trust-auditor]]**: Validates complexity, AST, HMAC, and CVEs before promotion

## Core Principles

1. **[[tdaid-methodology]]**: Tests must fail before implementations exist. Cryptographic `.qa_signature` HMAC gates every promotion.
2. **[[empirical-verification]]**: No modifications based on assumptions — trace physical evidence first.
3. **[[amnesia-sweep]] Defense**: Protect artifacts from `git clean -fd` destruction between evaluation runs.
4. **[[ephemeral-memory-handoff]]**: Persist architectural lessons in `executor_handoff.md` across sessions.

## Performance

The [[context-caching]] optimization (Era 5.1) achieved:
- **56% token reduction** across the evaluation suite
- **44% fewer inferences** on matched tests
- 11/11 evaluations passing at 100%

The [[solo-vs-swarm-benchmarks]] proved the fundamental [[tool-parallelism-bottleneck]]: the Swarm operates at ~4× the inference cost of a Solo agent due to irreducible agent-boundary serialization — but this overhead is the literal cost of adversarial verification that prevents hallucinated code from reaching production.

## Ecosystem

- **Sister repository**: `ngs-variant-validator` — domain-specific bioinformatics/FinOps layer using the hardened OS kernel
- **[[seqera-ai-integration]]**: First cross-agent integration for Nextflow/nf-core module QA
- **[[drift-registry]]**: Cross-file dependency tracking via `drift_enforcer.py`
- **[[evaluation-framework]]**: Automated benchmarking with 11 test categories and telemetry scoring

## Further Reading

- [Meta-Retrospective](../docs/retrospectives/2026-04-23_hvr_agentic_os_meta_retrospective.md) — The master chronological timeline
- [Era 5 Conclusion](../docs/retrospectives/2026-04-24_era_5_head_to_head_conclusion.md) — The definitive Solo vs Swarm verdict
- [Tool Parallelism Analysis](../docs/retrospectives/2026-04-25_tool_parallelism_bottleneck_analysis.md) — The deepest architectural analysis
