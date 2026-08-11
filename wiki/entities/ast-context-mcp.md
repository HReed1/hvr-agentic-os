---
title: "AST Context MCP Server"
date: 2026-08-11
category: entity
tags:
  - mcp
  - ast
  - context-engineering
  - token-efficiency
  - tooling
sources:
  - "[[mcp_servers/ast_context_mcp/README.md]]"
  - "[[.agents/skills/ast-context-engineer/SKILL.md]]"
  - "[[.agents/rules/ast-context-governance.md]]"
  - "[[docs/retrospectives/2026-08-11_wiki_db_infrastructure_and_v2_wiki_expansion.md]]"
last_ingested: 2026-08-11
---

The AST Context MCP Server is a standalone, local FastMCP server that provides token-efficient Abstract Syntax Tree parsing, skeleton extraction, and symbol isolation for Python and TypeScript/JavaScript codebases. It is a core component of the [[agentic-os]] context engineering layer, enabling agents to inspect large files without flooding the LLM context window. The companion [[context-benchmarking]] harness projects a **~75% input token reduction** using deterministic mock simulations, though this figure has not yet been validated with live Gemini inference (see [[context-benchmarking]] for details and roadmap).

## Tools

The server exposes four tools via the Model Context Protocol:

| Tool | Purpose |
|------|---------|
| `get_symbols` | Returns a JSON array of all declared classes, functions, methods, and types in a file, with start/end line coordinates. |
| `get_skeleton` | Generates a structural outline — replaces implementation bodies with `pass` (Python) or placeholders (TS/JS) while preserving signatures, decorators, type annotations, and docstrings. |
| `get_symbol_block` | Extracts the exact raw source lines for a single named symbol, filtering out everything else. |
| `get_hash` | Computes a normalized, comment- and spacing-insensitive SHA-256 hash of a file or specific symbol for semantic change tracking and drift detection. |

## Parsing Architecture

The server acts as a polyglot coordinator with two parsing backends:

- **Python files** (`.py`) are parsed natively using Python's standard `ast` module. Custom AST walkers extract skeletons, symbols, and compute docstring-free semantic hashes.
- **TypeScript/JavaScript files** (`.ts`, `.tsx`, `.js`, `.jsx`) are delegated to a local `ts_ast_parser.js` Node subprocess, which compiles source code into an AST using the official TypeScript Compiler API for formatting-insensitive token stream hashing and signature extraction.

Prerequisites are Python 3.11+ (with `uv` recommended) and Node.js for the TypeScript parser subprocess.

## The 80/20 Context Rule

The companion skill definition (`.agents/skills/ast-context-engineer/SKILL.md`) codifies the **80/20 context rule** for agent token budget management:

1. **80% Context Map (Skeletons):** Use lightweight AST skeletons for broad structural understanding — signatures, interfaces, types — at ~90% token reduction.
2. **20% Context Detail (Targeted Symbols):** Load full source code only for the specific functions or classes actively being modified or queried.

The token budget allocation varies by file size: files under 100 lines may be viewed in full, files between 100–300 lines should be skeleton-first, and files over 300 lines should use the symbols list plus skeleton before extracting individual targets.

## Governance Mandate

The governance rule (`.agents/rules/ast-context-governance.md`) enforces AST-first context loading as a hard mandate, not a suggestion:

- **AST Skeleton Priming:** For any source file exceeding 100 lines, the agent **must not** load the entire file. It must generate the skeleton first.
- **Targeted Symbol Reading:** Only the relevant symbol blocks should be loaded, not surrounding code.
- **Structural Pre-flight Checks:** Before modifying any symbol signature, agents must perform dependency impact analysis and verify semantic hashes via `get_hash`.
- **Precision Edits:** Edits must target only the specific symbol's lines — broad file rewrites are prohibited.

## IDE Integration

The server integrates with three agentic development environments:

- **Cursor IDE** — registered via Settings → Features → MCP → Add New MCP Server.
- **Claude Code** — registered via `claude mcp add ast-context-mcp`.
- **Antigravity IDE** — configured in `mcp_config.json` under `mcpServers`.

## History

The AST Context MCP Server was introduced in commit `69ef905` (2026-06-23), as part of the post-v2.0.0 context engineering push. It works in concert with the [[context-caching]] strategy to minimize [[token-tax]] across agent sessions, and its `get_hash` tool feeds semantic hashes into the [[drift-registry]] for change tracking.

## See Also

- [[context-caching]] — Broader caching strategies that complement AST-based context reduction
- [[token-tax]] — The cost model that AST skeletons directly address
- [[drift-registry]] — Consumes `get_hash` outputs for semantic drift detection
- [[agentic-os]] — Parent system architecture
