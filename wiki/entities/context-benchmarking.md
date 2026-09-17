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
  - "[[projects/context-benchmarking/run_benchmarks.py]]"
  - "[[docs/retrospectives/2026-06-23_ast_mcp_and_context_benchmarking.md]]"
  - "[[docs/retrospectives/2026-08-11_wiki_db_infrastructure_and_v2_wiki_expansion.md]]"
last_ingested: 2026-08-11
---

The Context Benchmarking Harness is a **deterministic simulation framework** for evaluating agent context engineering strategies. Located in `projects/context-benchmarking/`, it uses mock codebases with known-good solutions and a **monkeypatched mock LLM** (not live Gemini inference) to demonstrate what AST-guided context savings would look like across different task tiers. It is the largest single commit in the repository by line count.

## Architecture

The harness is orchestrated by `run_benchmarks.py`, a CLI entry point that runs benchmarks with mock LLM logic. It defines pairs of **original** and **solution** file contents inline, enabling deterministic evaluation without requiring a live LLM.

The benchmarking approach works by:

1. **Defining mock codebases** with intentionally flawed or baseline implementations (Python and JavaScript).
2. **Specifying known-good solutions** that represent the correct modifications an agent should produce.
3. **Simulating** both Scenario A (full-file reads) and Scenario B (AST-guided reads) with hardcoded token counts to demonstrate the scorecard pipeline.

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

The benchmarking harness was designed to validate the claims made by the [[ast-context-mcp]] server and the 80/20 context rule. In its current state, it **demonstrates the evaluation pipeline** using mock-derived token figures (75% reduction is a hardcoded parameter at `run_benchmarks.py:503`, not a measured outcome). The Offline Analyzer's "Theoretical Context Read Savings" section independently measures file sizes but reports 0% savings because the mock doesn't actually read files differently between scenarios.

The harness validates that the infrastructure works end-to-end (git isolation, scorecard generation, test execution), but **live Gemini inference has never been run** through this pipeline.

## Missing Modules

The real pipeline (`src/context_benchmarking/run_benchmarks.py`) imports three modules that are **not present on disk**:

| Module | Role | Status |
|--------|------|--------|
| `simulator.py` | `CoderAgentSimulator` — live Gemini reasoning loop | ❌ Missing |
| `analyzer.py` | `OfflineAnalyzer` — transcript token counting | ❌ Missing |
| `tools.py` | Scenario A/B tool implementations | ❌ Missing |

Only `dataset.py`, `git_manager.py`, and `reporter.py` exist in `src/`. This means the real pipeline cannot execute, and ~7 of the 12 test files would fail on import. These modules were either never committed or lost during the repo restructure.

## Roadmap: Live Inference Evaluation

To convert this from a demonstration scaffold to a genuine empirical validation tool:

1. **Implement the 3 missing modules** (`simulator.py`, `analyzer.py`, `tools.py`) to enable live Gemini inference
2. **Run Scenario A vs B** against real `gemini-2.5-flash` with actual token counting
3. **Compare measured savings** against the theoretical 75% claim from the mock
4. **Publish results** in a new retrospective with independently verified figures

This directly supports the [[evaluation-framework]] and would provide genuine ground-truth data for [[token-tax]] analysis.

## Documentation

The Context Benchmarking Harness has full documentation coverage:
- **Retrospective**: `docs/retrospectives/2026-06-23_ast_mcp_and_context_benchmarking.md` documents design decisions, architectural gotchas, and the mock vs real pipeline distinction
- **README**: `projects/context-benchmarking/README.md` provides setup, CLI usage, and adaptation guides
- **Wiki**: This page and [[ast-context-mcp]] provide cross-referenced entity documentation

## History

Introduced in commit `69ef905` (2026-06-23), part of the post-v2.0.0 context engineering push. It shares its commit with the [[ast-context-mcp]] server, suggesting both were developed as a coordinated effort to build and validate context optimization tooling.

## See Also

- [[ast-context-mcp]] — The context server whose strategies this harness benchmarks
- [[evaluation-framework]] — The broader evaluation infrastructure
- [[token-tax]] — The cost model that benchmarking results quantify
- [[context-caching]] — Complementary context strategies under test
