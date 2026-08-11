---
title: "Wiki Index"
date: 2026-06-02
category: index
tags:
  - wiki
  - index
---

# Wiki Index — hvr-agentic-os

> Content catalog for the agent-maintained knowledge base.

## Entities

| Page | Summary | Sources |
|------|---------|:-------:|
| [[agentic-os]] | The Zero-Trust Multi-Agent OS built on Google ADK — the project itself | 2 |
| [[ast-context-mcp]] | FastMCP server providing AST-based code parsing — ~75% token reduction (mock-projected) | 3 |
| [[context-benchmarking]] | Deterministic simulation framework for AST-guided context savings (mock LLM, 3 modules missing) | 2 |
| [[director-agent]] | Top-level orchestration node with macro-loop retry logic | 3 |
| [[dlp-proxy]] | PHI/HIPAA redaction interceptor stripping genomic data from LLM context | 2 |
| [[drift-enforcer]] | Python script enforcing architectural dependency contracts via git-hash tracking | 3 |
| [[drift-registry]] | Cross-file dependency tracking via `drift_enforcer.py` | 1 |
| [[evaluation-framework]] | Automated benchmarking infrastructure — `adk eval`, bash runners, scorecards | 4 |
| [[executor-agent]] | Code mutation engine constrained by TDAID chronological mandates | 3 |
| [[llm-wiki]] | Postgres-backed LLM Wiki — compounding knowledge base (Karpathy pattern) | 2 |
| [[qa-engineer-agent]] | Adversarial test gate and spec author under Spec-Driven TDD | 3 |
| [[seqera-ai-integration]] | First Antigravity × Seqera AI cross-agent integration for Nextflow/nf-core | 1 |
| [[session-lifecycle]] | Structured session workflows — `/session-start` and `/session-wrapup` | 3 |
| [[staging-airlock]] | The `.staging/` sandbox air-gap where all agent code executes | 2 |
| [[telemetry-engine]] | Trace extraction, token counting, and evaluation reporting subsystem | 2 |
| [[zero-trust-auditor]] | Final deployment gate — complexity, HMAC, AST, and CVE verification | 2 |
| [[zero-trust-interceptors]] | `zero_trust.py` monkeypatches — signal routing, loop termination, PHI scrubbing | 3 |

## Concepts

| Page | Summary | Sources |
|------|---------|:-------:|
| [[tdaid-methodology]] | Test-Driven AI Development — Red → Green → Refactor with cryptographic gates | 3 |
| [[token-tax]] | Exponential context bloat from shared conversational contexts | 2 |
| [[context-caching]] | Static/dynamic instruction split + Vertex AI caching — 56% token reduction | 2 |
| [[amnesia-sweep]] | Defense protocol protecting artifacts from `git clean -fd` destruction | 2 |
| [[tool-parallelism-bottleneck]] | Irreducible ~4× inference overhead from multi-agent tool segregation | 2 |
| [[solo-vs-swarm-benchmarks]] | Empirical head-to-head validation — Solo for speed, Swarm for safety | 3 |
| [[hierarchical-routing]] | SequentialAgent tree architecture replacing the Round-Table LoopAgent | 2 |
| [[anti-pattern-knowledge-graph]] | Documented systemic failure modes pre-loaded into agent context | 3 |
| [[ephemeral-memory-handoff]] | Cross-session persistence via `executor_handoff.md` ledger | 3 |
| [[empirical-verification]] | No-assumptions debugging — trace physical evidence before modifying code | 2 |

## Synthesis

_No synthesis pages yet. Pages will be created as queries are filed back._

---

*This index is automatically maintained by Antigravity agents. See the [wiki log](log.md) for activity history.*
