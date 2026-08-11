---
trigger: always_on
description: The absolute operational constitution and architectural constraints governing the Antigravity system.
---

# IDE Orchestrator (Antigravity) Operational Constitution

> **SCOPE**: This document acts as the absolute baseline architectural constraint and operational logic guide for the Antigravity (Gemini) orchestration agent interacting with the `hvr-agentic-os` workspace. All evaluations, code adjustments, and architectural modifications proposed by Antigravity MUST adhere perfectly to these foundational mandates.

## 1. The Amnesia Sweep Defense
When interacting with Swarm automation scripts (e.g. `bin/run_*_benchmark.sh`) that leverage hostile reset loops via `git clean -fd`:
* **Never assume untracked files will survive**. The orchestrator MUST actively track (`git add`) any vault directories (e.g. `docs/comparisons/`, `docs/evals/`) prior to the amnesia wipe.
* **Preserve Automation Logic**: Any direct orchestration script patches must be immediately staged (`git add`) so they are not silently unraveled by `git checkout -- .` executing mid-flight.

## 2. Zero-Trust Architectural Mapping
Never assume arbitrary `.py` files inside the `.staging/` airspace will natively merge into the root executable layer. The Zero-Trust Auditor strictly regulates whitelist deployments (`bin/`, `api/`, `tests/`).
* **Root Python Evasion**: Ensure evaluation prompts explicitly enforce structural namespace mappings (e.g., `bin/launch_kanban.py`) to bypass the Auditor's `shutil.rmtree` destruction protocol.

## 3. The Ephemeral Memory Handoff
Whenever Swarm nodes or local testing layers generate structural insights within the `.staging/` sandbox, ensure the outputs are dynamically pushed to `.staging/.agents/memory/executor_handoff.md` so they cleanly persist across the amnesia sweep sequence without bleeding into core project boundaries.

## 4. Strict CI/CD Hygiene
* **SAST CVE Exclusions**: Never arbitrarily pin external dependencies just to bypass non-exploitable local Agent LLM execution vulnerabilities. Use `.trivyignore` to logically bypass structural vulnerabilities trapped exclusively inside the zero-trust VPC.
* **Testing Global Integrity**: Ensure execution bounds are comprehensively vetted natively via `pytest tests/` prior to finalizing infrastructure mutations. 

## 5. Empirical Verification Pipeline
Before drafting system-wide patches or attempting to repair broken orchestration scripts, **empirically verify the bounds**.
* Do not inject workarounds based on abstract assumptions.
* Inspect physical file paths natively and trace the absolute CLI execution log boundaries. If a script parameter fails randomly, structurally read the deployment framework natively instead of attempting a blind fix.

## 6. Evaluation Matrix Synchronization
Whenever the IDE Orchestrator structurally modifies the underlying logic behind the Swarm (e.g., establishing a new `@workflow`, deprecating an existing agent role, or deploying a new `@skill`), you MUST explicitly and immediately synchronize the evaluation criteria.
* **Never leave evaluation matrices behind**: Legacy `.test.json` prompt definitions in `tests/adk_evals/` dictate how the Swarm operates during benchmarks. 
* If you design new rules without mapping those rules into the physical evaluation prompts, the Swarm will natively organically bypass your new governance and pass tests via brute force. 
* You are strictly mandated to execute a `grep` or search for stale terminologies or missing `@workflow` triggers in the testing suite payload whenever shifting core workflows.


## Wiki Maintenance Protocol

> This section governs how Antigravity agents maintain the `wiki/` knowledge base layer.
> The wiki is a persistent, compounding artifact — not a chatbot conversation.
> It gets richer with every source ingested and every question answered.

### Layer Architecture

```
docs/    → Human-authored source material. READ ONLY — never modify.
wiki/    → Agent-maintained knowledge base. You OWN this layer entirely.
raw/     → External sources for ingestion. READ ONLY — never modify.
```

### Wiki Directory Structure

```
wiki/
├── index.md       # Content catalog: every page listed with link, summary, source count
├── log.md         # Chronological activity record (append-only)
├── overview.md    # Living project synthesis — the "executive summary"
├── entities/      # Pages for key systems, tools, services, components
├── concepts/      # Pages for patterns, principles, methodologies, frameworks
└── synthesis/     # Cross-cutting analyses, comparisons, query results filed back
```

### Database Index

The wiki is backed by a Postgres database (`wiki` database, localhost:5432) that indexes all pages, cross-references, and activity. This lets you find relevant pages instantly via SQL instead of reading the entire index file.

> [!CAUTION]
> **Read vs. Write Access:** The `wiki-db` MCP server (`query` tool) is **read-only** — it can only execute `SELECT` queries. All write operations (`INSERT`, `UPDATE`, `DELETE`) **MUST** be executed via `psql` on the command line:
> ```bash
> psql -h localhost -p 5432 -d wiki -c "<your SQL statement>"
> ```
> Do NOT attempt writes through the MCP tool — they will silently fail with a read-only transaction error.

**Key tables:**
- `wiki_pages` — every wiki page with repo, path, title, category, tags[], summary, sources[]
- `wiki_links` — cross-references between pages (wikilinks, source references)
- `wiki_activity` — structured log of ingest/query/lint operations

**Key views:**
- `wiki_page_summary` — compact listing of all pages for quick orientation
- `wiki_orphans` — pages with no inbound links (lint target)
- `wiki_hubs` — most-linked pages (knowledge centers)

**Example agent queries (via MCP `query` tool):**
```sql
-- Find pages related to a topic
SELECT path, title, summary FROM wiki_pages
WHERE repo = 'hvr-agentic-os' AND ('security' = ANY(tags) OR title ILIKE '%security%');

-- Find all sources for a page
SELECT sources FROM wiki_pages WHERE repo = 'hvr-agentic-os' AND path = 'wiki/entities/nexus-api.md';

-- Find orphan pages needing links
SELECT * FROM wiki_orphans WHERE repo = 'hvr-agentic-os';

-- Find the most connected pages
SELECT * FROM wiki_hubs WHERE repo = 'hvr-agentic-os' LIMIT 10;

-- Recent activity
SELECT action, target, summary, created_at FROM wiki_activity
WHERE repo = 'hvr-agentic-os' ORDER BY created_at DESC LIMIT 10;
```

### Page Conventions

**Every wiki page** gets YAML frontmatter:
```yaml
---
title: "Page Title"
date: YYYY-MM-DD
category: entity | concept | synthesis
tags:
  - relevant-tag
sources:
  - "[[docs/path/to/source]]"
last_ingested: YYYY-MM-DD
---
```

**Cross-references**: Use `[[wikilinks]]` for all links within `wiki/`. Use standard markdown links `[text](../docs/path)` for references to `docs/` source material.

**Naming**: All wiki filenames use `kebab-case.md` (no date prefix needed for entity/concept pages).

### Ingest Workflow

When the user adds a new source document or asks you to ingest content:

1. **Read** the source document fully
2. **Discuss** key takeaways with the user
3. **Identify** entities (systems, tools, services) and concepts (patterns, principles)
4. For each entity/concept:
   - **Create** a new page in `wiki/entities/` or `wiki/concepts/` if it doesn't exist
   - **Update** the existing page if it does — note where new data confirms, extends, or contradicts existing content
5. **Update** `wiki/index.md` with any new page entries
6. **Append** to `wiki/log.md`:
   ```markdown
   ## [YYYY-MM-DD] ingest | Source Title
   - Source: `docs/path/to/source.md`
   - Created: [[new-page-name]] (if any)
   - Updated: [[existing-page-1]], [[existing-page-2]]
   - Key insight: One-line summary of what this source added
   ```
7. **Optionally update** `wiki/overview.md` if the source changes the project's big picture
8. **Update the database** — for each wiki page created or updated, upsert into `wiki_pages` and `wiki_links` via `psql` (the `wiki-db` MCP tool is read-only and cannot execute writes):
   ```bash
   psql -h localhost -p 5432 -d wiki -c "
   INSERT INTO wiki_pages (repo, path, title, category, tags, summary, sources, source_count, last_ingested)
   VALUES ('hvr-agentic-os', 'wiki/entities/page.md', 'Page Title', 'entity',
           ARRAY['tag1', 'tag2'], 'Summary text', ARRAY['docs/source.md'], 1, CURRENT_DATE)
   ON CONFLICT (repo, path) DO UPDATE SET
     title = EXCLUDED.title, tags = EXCLUDED.tags, summary = EXCLUDED.summary,
     sources = EXCLUDED.sources, source_count = EXCLUDED.source_count,
     last_ingested = EXCLUDED.last_ingested, updated_at = NOW();
   "
   ```
   > **Alternative:** Instead of individual SQL upserts, run the backfill script to sync all pages at once:
   > ```bash
   > python3 scripts/wiki_db_backfill.py --repo hvr-agentic-os --wiki-dir wiki
   > ```
9. **Log the activity** in the database (also via `psql`):
   ```bash
   psql -h localhost -p 5432 -d wiki -c "
   INSERT INTO wiki_activity (repo, action, target, summary, pages_created, pages_updated)
   VALUES ('hvr-agentic-os', 'ingest', 'docs/path/to/source.md', 'Ingested source; updated 3 pages', 0, 3);
   "
   ```

### Query Workflow

When the user asks a question against the wiki:

1. **Query the database** to find relevant pages (faster than reading index.md):
   ```sql
   SELECT path, title, summary FROM wiki_pages
   WHERE repo = 'hvr-agentic-os'
     AND (title ILIKE '%keyword%' OR 'tag' = ANY(tags) OR summary ILIKE '%keyword%');
   ```
2. **Read** the relevant wiki pages (synthesized knowledge, not raw sources)
3. **Synthesize** an answer with citations to wiki pages
4. If the answer is substantial or reusable:
   - **Offer** to file it as a new page in `wiki/synthesis/`
   - If filed, update `wiki/index.md`, the database, and append to `wiki/log.md`
5. **Log the query** in both `wiki/log.md` and the database:
   ```markdown
   ## [YYYY-MM-DD] query | "User's question"
   - Read: [[page-1]], [[page-2]]
   - Answer filed as: [[synthesis/answer-topic]] (or "answered in chat")
   ```

### Lint Workflow

Periodically (or when the user asks), health-check the wiki:

1. **Orphan pages**: Query `SELECT * FROM wiki_orphans WHERE repo = 'hvr-agentic-os';`
2. **Contradictions**: Flag claims in one page that contradict another
3. **Stale content**: Identify wiki pages whose source documents have been updated but the wiki page hasn't
4. **Missing pages**: Find entities or concepts frequently mentioned across pages but lacking their own dedicated page
5. **Missing cross-references**: Find pages that discuss the same topic but don't link to each other
6. **Check drift registry**: Read `docs/drift_registries/wiki.json` — for each wiki page, verify that source doc dependencies still exist and that `verified_commit` is current. Flag stale pages for re-ingestion.
7. **Report** findings and suggest fixes
8. **Append** to `wiki/log.md` and log in database:
   ```markdown
   ## [YYYY-MM-DD] lint | Health Check
   - Orphans found: N
   - Contradictions found: N
   - Stale pages: N
   - Missing pages suggested: N
   - Auto-fixed: description of fixes applied
   ```

### Guardrails

- **Never modify files in `docs/`** — that's the human-authored source layer
- **Never modify files in `raw/`** — those are immutable external sources
- **Always update `index.md`** when creating or deleting wiki pages
- **Always update the database** when creating, updating, or deleting wiki pages — use `psql` CLI or the backfill script, not the `wiki-db` MCP tool (which is read-only)
- **Always append to `log.md`** for every ingest, query, or lint operation
- **Flag contradictions explicitly** — don't silently overwrite one claim with another
- **Cite sources** — every claim in a wiki page should trace back to a document in `docs/` or `raw/`
- **Add `[[wikilinks]]`** — every new or updated page must cross-reference 2–5 related pages to build the knowledge graph

## Drift Registry Protocol

This project uses a drift registry system to track cross-file dependencies.
Registries live at `docs/drift_registries/*.json`. The enforcer script is at
`scripts/drift_enforcer.py`.

### When to add a registry entry

Add an entry when ANY of these occur:
1. A new source file is created that depends on or is depended upon by existing files
2. A new dependency relationship is discovered during development
3. An existing file gains a new consumer

### How to add an entry

1. Determine the correct domain registry (agent, infra, docs)
2. Ask: "If this file changes, what other files could break?"
3. Add a new object to the `entries` array with `verified_commit: null`
4. Run `python3 scripts/drift_enforcer.py --stamp` to initialize

### When to run the enforcer

- **End of every session** — before committing, run the enforcer to check for drift
- **Before merging PRs** — ensure no contracts have silently broken
- **Periodically** — as a hygiene check

### Stamping rules

> IMPORTANT: Only stamp at session end, never mid-session. Drift detected
> during development is expected — it means the enforcer is working. Save
> stamping for the wrapup step to preserve the system as a safety net.

### If drift is detected

1. Review the flagged files and their dependency reasons
2. If the changes are intentional: update the dependent files, then stamp
3. If the changes are unexpected: stop and consult the user
4. Always explain what was reviewed in the session retrospective

## Session Lifecycle

This project uses structured session workflows to prevent cold starts,
enforce drift checks, and compound knowledge across sessions.

### Starting a session

Run `/session-start` (or read `.agents/workflows/session-start.md`) at the
beginning of each engineering session. This:
1. Loads `wiki/overview.md` for project context
2. Scans the 2 most recent retrospectives for carryover items
3. Runs the drift enforcer (informational, not blocking)
4. Asks the user for session focus
5. Confirms session started with a structured briefing

### Ending a session

Run `/session-wrapup` (or read `.agents/workflows/session-wrapup.md`) at
the end of each session. This:
1. Stages and commits session changes
2. Enforces drift checks and stamps registries (the **only** correct stamping point)
3. Generates a retrospective in `docs/retrospectives/`
4. Optionally ingests significant work into `wiki/`
5. Commits docs, wiki, and stamped registries
6. Cleans up the ephemeral session drift log

### Rules

- **Never stamp drift registries mid-session.** Stamping happens only in
  the wrapup workflow.
- **Always generate a retrospective.** Even short sessions get a retro.
  Future sessions depend on these for context.
- **Don't push to remote automatically.** The user decides when to push.
- **Wiki ingest is optional.** Only ingest for architecturally significant
  sessions. Routine bug-fix sessions skip the wiki ingest step.
