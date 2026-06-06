---
title: "Evaluation Framework"
date: 2026-06-02
category: entity
tags:
  - evaluation
  - benchmarking
  - testing
  - adk-eval
sources:
  - "[[docs/retrospectives/2026-04-21_head_to_head_benchmarks.md]]"
  - "[[docs/retrospectives/2026-04-24_context_caching_optimization_results.md]]"
  - "[[docs/retrospectives/2026-04-24_era_5_head_to_head_conclusion.md]]"
  - "[[docs/guides/2026-04-21_head_to_head_evaluation_walkthrough.md]]"
last_ingested: 2026-06-02
---

# Evaluation Framework

The evaluation framework provides automated benchmarking infrastructure for the [[agentic-os]], testing both the Swarm and Solo paradigms across tiered complexity levels via ADK's `adk eval` command.

## Components

### Test Matrices (`tests/adk_evals/`)
JSON evaluation schemas defining task prompts, evaluator criteria, and expected outcomes. The suite spans multiple categories:

- **Engineering tests** (`test_eng_*`): Cyclomatic complexity, deterministic Playwright, strict TDAID coverage
- **Zero-Trust tests** (`test_zt_*`): Discovery loop breaker, hallucination recovery, human-in-the-loop mandate, PHI DLP redaction, Python AST validation, QA HMAC tampering, QA timeout breaker
- **Comparison tests** (`test_compare_*`): Small, Medium, Large, and Fullstack tiers

### Bash Orchestration (`bin/`)
- `run_head_to_head.sh` — Runs all comparison tests sequentially for Solo and Swarm
- `run_kanban_benchmark.sh` — Runs only the Fullstack Kanban benchmark
- `run_playwright_benchmark.sh` — Runs Playwright-specific evaluations
- `run_failed_evals.sh` — Reads the scorecard and retries only failed tests

### Telemetry Pipeline
- `utils/generate_global_eval_report.py` — Aggregates results into `GLOBAL_EVAL_SCORECARD.md`
- `utils/generate_comparison_report.py` — Generates `HEAD_TO_HEAD_SCORECARD.md`
- `utils/inject_telemetry.py` — Extracts inference and token metrics from ADK trace caches

## Evaluation Suite State (as of Era 5.1)

| Metric | Value |
|--------|-------|
| Total evaluations | 11 |
| Pass rate | 100% (11/11) |
| Total inferences | 162 |
| Total tokens | 1,955,411 |

This represents a **52.8% token reduction** from the pre-optimization baseline while adding 3 new tests.

## See Also

- [[solo-vs-swarm-benchmarks]] — The head-to-head comparison results
- [[context-caching]] — The optimization that dramatically reduced evaluation costs
- [[amnesia-sweep]] — The `git clean -fd` defense used between evaluation runs
