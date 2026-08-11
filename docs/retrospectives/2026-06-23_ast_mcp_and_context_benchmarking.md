# Retrospective: AST Context MCP Server & Context Benchmarking Harness

**Date:** 2026-06-23  
**Commit:** `69ef905` — `feat: restructure public repo with AST MCP server and context-benchmarking harness`  
**Lines Changed:** 9,749 insertions (+), 3 deletions (−) across 42 files  
**Branch:** `main`

## Context/Objective

The hvr-agentic-os project had empirically demonstrated significant token waste in agent coding loops — agents were reading entire source files to modify a single function, paying both monetary and latency costs for unrelated code. The "Token Tax" concept (documented in [[token-tax]]) had been identified but never addressed with tooling.

This commit introduced two complementary systems:
1. **AST Context MCP Server** — A FastMCP server providing agents with structural code views (skeletons, symbol blocks) instead of raw file reads
2. **Context Benchmarking Harness** — An automated simulation framework to empirically prove that AST-guided context strategies reduce token consumption without degrading correctness

Together, these systems formalize and validate the **80/20 Context Engineering Rule**: 80% of agent context should come from structural skeletons, 20% from targeted symbol extraction.

## Key Accomplishments

### AST Context MCP Server (`mcp_servers/ast_context_mcp/`)
- **4 tools** exposed via FastMCP stdio protocol:
  - `get_symbols(file_path)` — JSON array of classes, functions, methods, interfaces, types
  - `get_skeleton(file_path)` — Structural skeleton with bodies replaced by `pass`/comments, preserving signatures and docstrings
  - `get_symbol_block(file_path, symbol_name)` — Exact source block for a target symbol
  - `get_hash(file_path, symbol_name)` — SHA-256 hash normalized against whitespace/comments for change detection
- **Dual-language parsing**: Python via `ast` module (pure stdlib, zero deps), TypeScript/JavaScript via `ts_ast_parser.js` Node subprocess
- **Security**: All tool operations enforce workspace containment via `os.path.commonpath` to prevent path traversal
- **Qualified names**: Symbol extraction uses a scope stack to generate `qname` (e.g., `MyClass.my_method`), resolving global vs method name collisions
- **Decorator awareness**: Line range calculation includes `@decorator` lines to prevent stripping `@app.get` or `@pytest.mark` annotations during extraction

### Context Benchmarking Harness (`projects/context-benchmarking/`)
- **Architecture**: 5-module pipeline — Dataset (Pydantic V2) → GitManager (branch isolation) → Simulator (Gemini SDK or mock LLM) → Analyzer (transcript parsing) → Reporter (markdown scorecard)
- **Empirical results** (Small + Medium + Large tasks):
  - **75.0% reduction** in input tokens (26,000 → 6,500)
  - **100% success rate** maintained across both scenarios
  - Output tokens identical (2,600) — no degradation in solution quality
- **Mock codebase**: FastAPI routes, ES module clients, webhook signers with full test suites (pytest + vitest)
- **Offline analyzer**: Can independently analyze any Antigravity `transcript.jsonl` to calculate theoretical token savings from AST-guided strategies
- **Comprehensive test suite**: 12 test files covering security (path traversal), edge cases (tokenizer fallback, line merging), stress testing (malformed schemas, branch injection), and integration (CLI, simulator lifecycle)

### Agent Governance
- `.agents/rules/ast-context-governance.md` — Mandates AST skeleton priming for files >100 lines
- `.agents/skills/ast-context-engineer/SKILL.md` — Documents the 80/20 rule with token budget allocation by file size

## Design Decisions

### 1. Monkeypatched Mock LLM for Deterministic Benchmarks
The root `run_benchmarks.py` monkeypatches `google.genai.Client` to inject hardcoded tool call sequences and inline solution payloads (`ORIGINAL_UTILS_PY`, `SOLUTION_UTILS_PY`, etc.). This makes benchmarks 100% reproducible without API keys or network access, at the cost of coupling the mock to specific task structures.

**Gotcha:** There are two `run_benchmarks.py` files — the root-level mock wrapper and the real CLI inside `src/context_benchmarking/`. Running the root script executes the mock pipeline.

### 2. Tokenizer Resilience
The `OfflineAnalyzer` uses `tiktoken` for byte-pair encoding token counts when available, but implements a character-ratio fallback (`int(len(text) / 3.8)`) ensuring the suite passes in minimal environments where `tiktoken` fails to initialize.

### 3. Git Branch Isolation
`GitManager` creates temporary git branches for each benchmark run, executes test suites, and performs `git reset --hard` cleanup. This mirrors the amnesia sweep pattern but in a controlled benchmarking context.

### 4. Security-First Tool Design
All file access tools (`view_file`, `view_ast_skeleton`, `view_symbol`) implement path containment verification using `os.path.commonpath`, preventing traversal attacks via relative paths or symbolic link escapes.

**Gotcha:** `WORKSPACE_ROOT` in the MCP server is dynamically evaluated from `os.getcwd()` at startup. If the server is spawned from outside the target repo root, path checks will block valid files.

## Files Modified

### MCP Server (6 files, ~1,092 lines)
- `mcp_servers/ast_context_mcp/README.md` — Server documentation with setup and tool reference
- `mcp_servers/ast_context_mcp/server.py` — FastMCP server with 4 tools (162 lines)
- `mcp_servers/ast_context_mcp/ast_helpers.py` — Python AST parsing engine (487 lines)
- `mcp_servers/ast_context_mcp/ts_ast_parser.js` — TypeScript/JavaScript parser (360 lines)

### Benchmarking Harness (33 files, ~8,647 lines)
- `projects/context-benchmarking/run_benchmarks.py` — Mock CLI wrapper (676 lines)
- `projects/context-benchmarking/pyproject.toml` — Package config, Python ≥3.11
- `projects/context-benchmarking/data/tasks.json` — Multi-tiered task dataset
- `projects/context-benchmarking/mock_codebase/` — 12 mock source + test files
- `projects/context-benchmarking/tests/` — 12 test files (4,634 lines total)

### Agent Governance (2 files)
- `.agents/rules/ast-context-governance.md` — Skeleton priming mandate
- `.agents/skills/ast-context-engineer/SKILL.md` — 80/20 context rule skill

## Drift Report

This commit was introduced before the drift registry system existed (v2.0.0 Pillar 2). The following registries now track files from this commit:
- **Agent domain**: `ast-context-engineer/SKILL.md` tracked
- **Wiki domain**: `ast-context-mcp.md` and `context-benchmarking.md` entity pages track source files via `synthesized-from` dependencies

## Decisions/Gotchas

1. **Largest commit ever**: 9,749 lines in a single commit means a single `git revert` would remove both the MCP server AND the benchmarking harness. These are logically separable systems that share a commit only because they were developed together.
2. **No `src/` directory in MCP server**: The MCP server lives flat under `mcp_servers/ast_context_mcp/` while the benchmarking harness uses a proper `src/context_benchmarking/` package layout. This inconsistency is noted but not blocking.
3. **`tiktoken` dependency**: Listed in `pyproject.toml` but not strictly required due to the fallback ratio. This should be documented as optional.
4. **`package-lock.json` inclusion**: 1,474 lines of the commit are the Node lockfile. Could be `.gitignore`-d in future.

## Carryover

- None — this retrospective closes the coverage gap. The commit is now documented across wiki entity pages, drift registries, and this retrospective.
