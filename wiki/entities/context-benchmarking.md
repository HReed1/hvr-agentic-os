---
title: "Context Benchmarking Harness"
date: 2026-08-11
category: entity
tags:
  - benchmarking
  - context-engineering
  - testing
  - evaluation
sources:
  - "[[docs/projects/context-benchmarking/run_benchmarks.py]]"
last_ingested: 2026-08-11
---

The Context Benchmarking Harness is a testing framework for evaluating agent context engineering strategies. Located in `projects/context-benchmarking/`, it uses mock codebases with known-good solutions to measure whether agents can perform targeted code modifications under different context loading strategies. It is the largest single commit in the repository by line count and currently has no retrospective or release coverage.

## Architecture

The harness is orchestrated by `run_benchmarks.py`, a CLI entry point that runs benchmarks with mock LLM logic. It defines pairs of **original** and **solution** file contents inline, enabling deterministic evaluation without requiring a live LLM.

The benchmarking approach works by:

1. **Defining mock codebases** with intentionally flawed or baseline implementations (Python and JavaScript).
2. **Specifying known-good solutions** that represent the correct modifications an agent should produce.
3. **Measuring** whether an agent's context strategy enables it to identify and apply the correct function-level changes.

## Mock Codebase Structure

The harness includes test scenarios for function-level code modifications:

- **`format_log_message`** (Python `utils.py`) — Tests whether agents can upgrade a log formatter from raw timestamp floats to ISO 8601, add input validation, sanitize newline injection, and switch metadata serialization from `str()` to compact JSON.
- **`routes`** (Python `routes.py`) — Tests FastAPI route modifications against a mock in-memory database with `TaskItem` Pydantic models.
- Additional JavaScript test scenarios covering equivalent modification patterns.

## Scale

The harness is substantial in scope:

| Metric | Count |
|--------|-------|
| Mock codebase files | 12 |
| Test files | 11 |
| Main orchestrator | 1 (`run_benchmarks.py`) |
| Total lines | 9,749 |

This makes it the largest single commit in the repository's history — all 9,749 lines were introduced in commit `69ef905` (2026-06-23), alongside the [[ast-context-mcp]] server.

## Relationship to AST Context Engineering

The benchmarking harness exists to empirically validate the claims made by the [[ast-context-mcp]] server and the 80/20 context rule. By running agents against the same mock codebases with and without AST-based context strategies, the harness can measure:

- **Token consumption** — How many tokens does the agent use to reach the correct solution?
- **Accuracy** — Does the agent modify the correct function without breaking adjacent code?
- **Precision** — Are edits scoped to the target symbol, or do they bleed into unrelated lines?

This directly supports the [[evaluation-framework]] and provides ground-truth data for [[token-tax]] analysis.

## Coverage Gap

As of this writing, the Context Benchmarking Harness has **no retrospective or release documentation**. It was introduced post-v2.0.0 and has not been covered in any session retrospective or release notes. This makes it one of the least documented subsystems relative to its size.

## History

Introduced in commit `69ef905` (2026-06-23), part of the post-v2.0.0 context engineering push. It shares its commit with the [[ast-context-mcp]] server, suggesting both were developed as a coordinated effort to build and validate context optimization tooling.

## See Also

- [[ast-context-mcp]] — The context server whose strategies this harness benchmarks
- [[evaluation-framework]] — The broader evaluation infrastructure
- [[token-tax]] — The cost model that benchmarking results quantify
- [[context-caching]] — Complementary context strategies under test
