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
  - "[[docs/reference/llm-wiki-antigravity.md]]"
  - "[[mcp_servers/ast_context_mcp/README.md]]"
last_ingested: 2026-08-11
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

## v2.0.0 — Portable Agentic Workflows & Compounding Memory

The v2.0.0 release (2026-06-15) shifted the framework from a multi-agent sandbox into a general-purpose toolkit. Three pillars were introduced:

1. **[[llm-wiki]]**: A Postgres-backed implementation of Andrej Karpathy's LLM Wiki pattern — incrementally building and maintaining a persistent, interlinked knowledge base instead of re-deriving answers via RAG. The agent writes the wiki; you ask the questions.

2. **[[drift-registry]]** + **[[drift-enforcer]]**: Machine-readable JSON contracts (4 domain registries: agent, docs, infra, wiki) linking source files to downstream dependencies, with `drift_enforcer.py` comparing git hashes to detect staleness. Stamping is exclusive to session boundaries.

3. **[[session-lifecycle]]**: Structured session workflows (`/session-start`, `/session-wrapup`) with auto-context loading, drift checks, retrospective generation, and optional wiki ingest — creating a self-reinforcing loop where every significant session enriches the knowledge base.

## Post-v2.0.0 Unreleased Work

Two major subsystems were introduced in commit `69ef905` (2026-06-23) but remain unreleased:

- **[[ast-context-mcp]]**: A standalone FastMCP server providing AST-based code parsing for Python and TypeScript/JavaScript. Four tools (`get_symbols`, `get_skeleton`, `get_symbol_block`, `get_hash`) enable targeted symbol extraction instead of full-file reads, with a theoretical ~75% token reduction projected by mock simulations (not yet validated with live inference).

- **[[context-benchmarking]]**: A deterministic simulation framework (9,749 lines — the largest single commit in the repo) demonstrating AST-guided context savings with mock LLM logic. The real inference pipeline is partially implemented (3 core modules missing). See the wiki entity page for roadmap.

## Ecosystem

- **Sister repository**: `ngs-variant-validator` — domain-specific bioinformatics/FinOps layer using the hardened OS kernel
- **[[seqera-ai-integration]]**: First cross-agent integration for Nextflow/nf-core module QA
- **[[evaluation-framework]]**: Automated benchmarking with 11 test categories and telemetry scoring

## Further Reading

- [Meta-Retrospective](../docs/retrospectives/2026-04-23_hvr_agentic_os_meta_retrospective.md) — The master chronological timeline
- [Era 5 Conclusion](../docs/retrospectives/2026-04-24_era_5_head_to_head_conclusion.md) — The definitive Solo vs Swarm verdict
- [Tool Parallelism Analysis](../docs/retrospectives/2026-04-25_tool_parallelism_bottleneck_analysis.md) — The deepest architectural analysis
- [LLM Wiki Reference Guide](../docs/reference/llm-wiki-antigravity.md) — The full wiki implementation spec
