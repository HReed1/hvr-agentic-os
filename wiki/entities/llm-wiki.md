---
title: "LLM Wiki"
date: 2026-08-11
category: entity
tags:
  - wiki
  - knowledge-management
  - postgres
  - obsidian
  - karpathy
sources:
  - "[[docs/reference/llm-wiki-antigravity]]"
last_ingested: 2026-08-11
---

The LLM Wiki is the Postgres-backed, agent-maintained knowledge base at the heart of the [[agentic-os]] project. It implements [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the core insight that **compiling knowledge once into a persistent wiki beats re-deriving it via RAG on every query**. The wiki is a compounding artifact: it gets richer with every source ingested and every question answered. As the reference guide puts it: "Obsidian is the IDE. The agent is the programmer. The wiki is the codebase."

## Architecture

The system has three content layers and one infrastructure layer.

### Content Layers

| Layer | Path | Ownership | Purpose |
|-------|------|-----------|---------|
| Raw sources | `raw/` | Immutable | External documents — web clips, transcripts, PDFs. Agent reads but never modifies. |
| Project docs | `docs/` | Human-authored | Architecture docs, decision records, retrospectives, guides. Agent reads but never modifies. |
| Wiki | `wiki/` | Agent-maintained | Synthesized, interlinked markdown files organized into three categories. |

### Wiki Categories

- **`entities/`** — pages for concrete things: systems, tools, services, components, APIs
- **`concepts/`** — pages for abstract things: patterns, principles, methodologies, frameworks
- **`synthesis/`** — cross-cutting analyses, comparisons, and query results filed back into the wiki

### Special Files

Three special files live at the wiki root:

1. **`index.md`** — content catalog with links, summaries, and source counts
2. **`log.md`** — chronological append-only activity record
3. **`overview.md`** — living executive summary of the entire knowledge base

### Infrastructure Layer

The infrastructure consists of the **GEMINI.md schema** (the Wiki Maintenance Protocol section that tells the agent how the wiki is structured and what workflows to follow) and a **Postgres database** that indexes all pages, cross-references, and activity into queryable SQL. The database uses three tables — `wiki_pages`, `wiki_links`, `wiki_activity` — and three helper views: `wiki_page_summary` (compact listing), `wiki_orphans` (pages with no inbound links), and `wiki_hubs` (most-linked pages).

> **Read vs. Write:** The `wiki-db` MCP server is **read-only** — it can only execute `SELECT` queries. All writes (`INSERT`, `UPDATE`, `DELETE`) must be executed via `psql` CLI or the `wiki_db_backfill.py` script. Attempting writes through the MCP tool silently fails with a read-only transaction error.

## Operations

The wiki supports three core operations, each logged in both `log.md` and the `wiki_activity` database table:

### Ingest

Drop a source into `raw/` or point the agent at a doc in `docs/`. The agent reads the source fully, identifies entities and concepts, creates or updates wiki pages (noting where new data confirms, extends, or contradicts existing content), updates `index.md`, appends to `log.md`, and upserts the database. A single source typically touches 5–15 wiki pages.

### Query

Ask questions against the wiki. The agent queries the database to find relevant pages via SQL (milliseconds, not full-file scans), reads the synthesized wiki pages, and synthesizes an answer with citations. Substantial answers get filed as `wiki/synthesis/` pages — explorations compound in the knowledge base just like ingested sources.

### Lint

Periodically health-check the wiki: find orphan pages (`wiki_orphans` view), flag contradictions, detect stale content via source-doc change timestamps, identify missing pages for frequently-mentioned entities, and check for missing cross-references. Optionally integrates with the [[drift-registry]] for git-hash-based staleness detection.

## Session Integration

The wiki integrates with the [[agentic-os]] session lifecycle via [[ephemeral-memory-handoff]]:

- **Session start:** Read `wiki/overview.md` to establish project context before setting goals — the agent gets a pre-compiled understanding of the project state in a single file.
- **Session wrapup:** Significant sessions (architectural changes, new features, security work) get their retrospectives ingested into the wiki. Routine bug-fix sessions are skipped.

This creates a self-reinforcing loop: every significant engineering session enriches the wiki automatically.

## Drift Integration

The wiki has a dedicated `wiki.json` drift registry tracked by the [[drift-registry]] system. Each wiki page can declare `synthesized-from` dependencies on its source documents. When a source doc changes, the [[drift-enforcer]] automatically flags the dependent wiki page as stale — the staleness chain propagates: `code changes → doc stale → wiki stale → flagged for re-ingest`.

## Why This Beats RAG

The fundamental advantage is **persistent knowledge accumulation**. RAG re-derives answers from scratch every query with no cross-referencing, no contradiction detection, and wasted context-window tokens on navigation. The LLM Wiki pre-compiles all of this: cross-references exist in `wiki_links`, contradictions are caught during lint, and the agent reads 3–5 synthesized pages instead of 50 raw chunks. The database query finds pages in milliseconds. The maintenance burden is near-zero because the agent does all the bookkeeping.

## Implementation Context

The LLM Wiki is **Pillar 1 of the v2.0.0 architecture**. The reference implementation guide is at [docs/reference/llm-wiki-antigravity.md](docs/reference/llm-wiki-antigravity.md). The system scales from personal use (<500 pages, local Postgres) through team (500–2K, cloud Postgres + `pgvector`) to enterprise (10K+, multi-agent router architecture). The database schema is identical at every scale — only the deployment topology changes.
