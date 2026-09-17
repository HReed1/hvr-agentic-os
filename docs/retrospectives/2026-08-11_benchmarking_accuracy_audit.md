# Retrospective: Benchmarking Accuracy Audit & Wiki Corrections

**Date:** 2026-08-11  
**Commits:** `7f70523`, `2f39a8e`, `203d660`  
**Branch:** `doc_updates`

## Context/Objective

This session was a direct continuation of the previous wiki-db infrastructure session. The primary goals were:
1. Complete carryover item 2: write a formal retrospective for the context-benchmarking harness (commit `69ef905`)
2. Audit the actual benchmarking results on disk
3. Correct any inaccuracies discovered during the audit

## Key Accomplishments

### Carryover Resolution
- **Created formal retrospective** for commit `69ef905` — the 9,749-line AST MCP + context benchmarking introduction
- Updated `wiki/entities/context-benchmarking.md` to reference the new retrospective as a source
- Appended ingest entries to `wiki/log.md` and synced the wiki database

### Benchmarking Accuracy Audit (Unplanned — Highest Value)
- **Discovered the results on disk** (`projects/context-benchmarking/results/`) are from a mock LLM pipeline with hardcoded token values, not live Gemini inference
- **Traced the exact mechanism**: `run_benchmarks.py:503` sets `prompt_tokens = 2000` for Scenario A and `500` for Scenario B — the "75% reduction" is `(2000-500)/2000`, a design parameter
- **Discovered 3 missing core modules**: `simulator.py`, `analyzer.py`, and `tools.py` are imported by the real CLI and 7 test files but don't exist on disk, making the live inference pipeline non-functional
- **Cross-referenced with hvr-informatics diagnosis**: The sister repo's agent had already concluded "The harness is a simulator with deterministic mock values, validated against real tiktoken counts of actual files. It was never run with live Gemini inference."

### Wiki Corrections (5 files)
- **wiki/entities/context-benchmarking.md**: Rewritten as "deterministic simulation framework", added Missing Modules table and 4-item Roadmap section
- **wiki/entities/ast-context-mcp.md**: Qualified 75% as "mock-projected, not yet validated with live inference"
- **wiki/overview.md**: Qualified both AST and benchmarking descriptions
- **wiki/index.md**: Updated both entity summaries
- **docs/retrospectives/2026-06-23**: Corrected from "empirical results" to "mock-derived figures", added gotchas 5-6, replaced "no carryover" with roadmap

## Files Modified

### Created
- `docs/retrospectives/2026-06-23_ast_mcp_and_context_benchmarking.md` — Formal retrospective for the benchmarking commit

### Modified
- `wiki/entities/context-benchmarking.md` — Major rewrite for accuracy
- `wiki/entities/ast-context-mcp.md` — Qualified 75% claim
- `wiki/overview.md` — Qualified both entries
- `wiki/index.md` — Updated 2 entries
- `wiki/log.md` — Appended 2 activity entries
- `docs/drift_registries/wiki.json` — Stamped at wrapup

## Drift Report

- **Agent**: 12/12 clean ✅
- **Docs**: 7/7 clean ✅
- **Infra**: 6/6 clean ✅
- **Wiki**: 30/30 stamped (3 drifted from our session edits + 6 newly registered pages from previous session, all intentional) ✅

## Decisions/Gotchas

1. **Radical honesty over flattering metrics**: The 75% token reduction was presented across 4 wiki surfaces as an empirical result. Rather than leave it ambiguous, we corrected all instances to clearly state it's a mock-derived design parameter. This is uncomfortable but correct — the wiki is a knowledge base, not marketing material.

2. **Missing modules are a genuine gap**: The 3 missing source files (`simulator.py`, `analyzer.py`, `tools.py`) mean the test suite is partially broken and the real pipeline can't run. This was either a commit oversight or a restructure casualty from `69ef905`.

3. **hvr-informatics cross-reference validated the finding**: The sister repo's agent independently reached the same conclusion about the mock nature of the results, providing a second opinion before we modified any files.

## Carryover

1. **Implement the 3 missing modules** (`simulator.py`, `analyzer.py`, `tools.py`) to enable live Gemini inference through the benchmarking harness
2. **Run live Scenario A vs B benchmarks** against real `gemini-2.5-flash` with actual token counting
3. **Compare measured savings** against the theoretical 75% mock figure and publish independently verified results
4. **Fix ~7 broken test files** that import missing modules
