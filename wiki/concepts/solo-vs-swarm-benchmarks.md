---
title: "Solo vs Swarm Benchmarks"
date: 2026-06-02
category: concept
tags:
  - benchmarking
  - evaluation
  - solo
  - swarm
  - empirical
sources:
  - "[[docs/retrospectives/2026-04-21_head_to_head_benchmarks.md]]"
  - "[[docs/retrospectives/2026-04-24_era_5_head_to_head_conclusion.md]]"
  - "[[docs/retrospectives/2026-04-25_tool_parallelism_bottleneck_analysis.md]]"
last_ingested: 2026-06-02
---

# Solo vs Swarm Benchmarks

The Solo vs Swarm Head-to-Head Benchmark is the definitive empirical validation of the [[agentic-os]] architecture, pitting a monolithic "God-Mode" agent against the hierarchical Zero-Trust Swarm across four complexity tiers.

## The Paradigms

1. **Solo God-Mode Agent**: A single `SequentialAgent` possessing every tool, rule, and capability. Constrained only by context windows.
2. **Autonomous Swarm**: A rigid Zero-Trust hierarchy (Director → Executor → QA Engineer → Auditor) with specialized toolsets and [[tdaid-methodology]] verification.

## Final Scorecard (Era 5)

| Benchmark | Swarm Inf | Swarm Tokens | Solo Inf | Solo Tokens |
|-----------|:---------:|:------------:|:--------:|:-----------:|
| Small     | 19        | 218,911      | 14       | 164,602     |
| Medium    | 21        | 189,595      | 8        | 107,108     |
| Large     | 25        | 232,295      | 6        | 89,341      |
| Fullstack | 34        | 809,823      | 16       | 418,968     |

Both paradigms achieved **100% pass rates** across all tiers.

## Key Findings

### The Inference Inversion
In early benchmarks, an interesting **inference inversion** occurred at scale: as task complexity increased, the Solo agent started spending more iterations parsing its own bloated history. The Swarm's ephemeral amnesia gave it a footprint advantage on large tasks (18 inferences vs Solo's 26). This advantage disappeared in Era 5 with [[context-caching]].

### Code Quality Differential
- **Solo**: Highly tailored to UX design, modular MVC architecture, larger templates with glassmorphism rendering
- **Swarm**: Utilitarian, explicitly constrained by token limits, brutalist HTML tuned to pass QA assertions. But adversarial testing produced more aggressive E2E coverage (125-line tests vs Solo's 98-line tests).

### The "Paralysis by Protocol" Paradox
The Swarm's rigidity is both asset and vulnerability. A contradictory debugging constraint in the QA prompt caused a 136-inference infinite loop consuming 4.2M tokens. Minor prompt contradictions cause adversarial sub-agents to violently loop against each other.

## Verdict

1. **For bootstrapping & discovery**: Solo is strictly superior (faster, cheaper, more aesthetic output)
2. **For Zero-Trust CI/CD pipelines**: Swarm is the sole viable option (adversarial verification guarantees hallucinated code never escapes `.staging/`)

## See Also

- [[tool-parallelism-bottleneck]] — The structural analysis of why the Swarm is inherently slower
- [[token-tax]] — The original context bloat problem
- [[evaluation-framework]] — The infrastructure powering the benchmarks
- [[context-caching]] — Optimization applied between benchmark eras
