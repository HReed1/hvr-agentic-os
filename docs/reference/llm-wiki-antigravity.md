# LLM Wiki — Antigravity Edition

A battle-tested implementation of Andrej Karpathy's LLM Wiki pattern, customized for [Google Antigravity](https://github.com/google/antigravity) agents with a Postgres metadata index, drift-aware staleness detection, and session-integrated workflows.

This is an implementation guide. Copy this file into your project and let your Antigravity agent bootstrap the wiki infrastructure. The agent will create the directories, database schema, and GEMINI.md protocol — then you start ingesting.

> **Attribution:** This builds on [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern. The core idea — compiling knowledge into a persistent wiki instead of re-deriving it via RAG — is his. Everything below is our opinionated implementation of that idea for Antigravity agents.

## The core idea

Most people's experience with LLMs and documents looks like RAG: you upload a collection of files, the LLM retrieves relevant chunks at query time, and generates an answer. This works, but the LLM is rediscovering knowledge from scratch on every question. There's no accumulation. Ask a subtle question that requires synthesizing five documents, and the LLM has to find and piece together the relevant fragments every time. Nothing is built up.

The idea here is different. Instead of just retrieving from raw documents at query time, the LLM **incrementally builds and maintains a persistent wiki** — a structured, interlinked collection of markdown files that sits between you and the raw sources. When you add a new source, the LLM doesn't just index it for later retrieval. It reads it, extracts the key information, and integrates it into the existing wiki — updating entity pages, revising topic summaries, noting where new data contradicts old claims, strengthening or challenging the evolving synthesis.

**The wiki is a persistent, compounding artifact.** The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read. The wiki keeps getting richer with every source you add and every question you ask.

You never write the wiki yourself — the Antigravity agent writes and maintains all of it. You're in charge of sourcing, exploration, and asking the right questions. The agent does the summarizing, cross-referencing, filing, and bookkeeping. In practice, you have Antigravity open on one side and Obsidian open on the other. The agent makes edits, and you browse the results in real time — following links, checking the graph view, reading the updated pages.

**Obsidian is the IDE. The agent is the programmer. The wiki is the codebase.**

## Architecture

There are four layers (three content layers + one infrastructure layer):

### Content layers

**Raw sources** (`raw/`) — your curated collection of external source documents. Articles clipped via Obsidian Web Clipper, meeting transcripts, PDFs, podcast notes, images. These are immutable — the agent reads from them but never modifies them.

**Project documentation** (`docs/`) — your human-authored source material. Architecture docs, decision records, retrospectives, guides, security audits. The agent reads these during ingest but never modifies them. This is your source of truth for project knowledge.

**The wiki** (`wiki/`) — agent-generated markdown files organized into three categories:
- `entities/` — pages for concrete things: systems, tools, services, components, APIs
- `concepts/` — pages for abstract things: patterns, principles, methodologies, frameworks
- `synthesis/` — cross-cutting analyses, comparisons, and query results filed back into the wiki

Plus three special files:
- `index.md` — content catalog with links, summaries, and source counts
- `log.md` — chronological append-only activity record
- `overview.md` — living executive summary of the entire knowledge base

### Infrastructure layer

**The schema** (`GEMINI.md`) — tells the Antigravity agent how the wiki is structured, what the conventions are, and what workflows to follow. This is the key configuration file — it's what makes the agent a disciplined wiki maintainer rather than a generic chatbot. You and the agent co-evolve this over time.

**The database** (Postgres) — a metadata index that mirrors the wiki's structure in queryable SQL. Every wiki page gets a row with its title, category, tags, summary, sources, and timestamps. Cross-references between pages are tracked as link records. This lets the agent find relevant pages via SQL in milliseconds instead of reading the entire `index.md` file — critical as the wiki grows past ~150 pages.

## Directory structure

### Per-project layout

Each project that uses the wiki gets this structure:

```
your-project/
├── GEMINI.md              # Agent schema — wiki protocol lives here
├── docs/                  # Human-authored project documentation
│   ├── architecture/
│   ├── decisions/
│   ├── guides/
│   ├── retrospectives/
│   ├── security/
│   └── ...
├── raw/                   # External sources for ingestion
│   ├── articles/          # Web articles clipped via Obsidian Web Clipper
│   ├── transcripts/       # Meeting notes, interviews, call recordings
│   └── assets/            # Images, PDFs, diagrams
├── wiki/                  # Agent-maintained knowledge base
│   ├── index.md           # Content catalog (auto-maintained)
│   ├── log.md             # Activity record (append-only)
│   ├── overview.md        # Living project synthesis
│   ├── entities/          # Systems, tools, services, components
│   ├── concepts/          # Patterns, principles, methodologies
│   └── synthesis/         # Cross-cutting analyses, filed query results
└── .obsidian/             # Obsidian vault configuration
```

### Infrastructure Options: Single-Repo vs. Multi-Repo

Depending on your workflow, you can run the LLM Wiki in one of two configurations:

#### Option A: Single-Repo Setup (Simplest)
If you only want to manage a wiki for a single repository, keep the database scripts (`wiki_db_init.py`, `wiki_db_backfill.py`) directly inside your project's `scripts/` directory:
```
your-project/
├── scripts/
│   ├── wiki_db_init.py      # Initialize the local database schema
│   └── wiki_db_backfill.py  # Index your local wiki pages
├── wiki/
└── ...
```

#### Option B: Multi-Repo Setup (Centralized Infrastructure)
If you want to index wikis across multiple separate projects in a shared Postgres database, centralize the scripts in a dedicated infrastructure repository (e.g., `your-infra-repo`). This keeps scripts in one place and avoids duplicating them:
```
your-infra-repo/
├── scripts/
│   ├── wiki_db_init.py      # Initialize the shared database schema
│   └── wiki_db_backfill.py  # Index any project's wiki directory
└── docs/
    └── reference/
        └── llm-wiki-antigravity.md  # Reference guide
```

#### Usage Examples
```bash
# Initialize the database (run once)
python3 scripts/wiki_db_init.py --database wiki --host localhost --port 5432

# Backfill/index a repository's wiki (run to sync)
python3 scripts/wiki_db_backfill.py --repo my-project-repo --wiki-dir /path/to/my-project/wiki --host localhost --port 5432
```

## Database schema

The database uses three tables and three helper views:

```sql
-- Every wiki page gets a row
CREATE TABLE wiki_pages (
    id            SERIAL PRIMARY KEY,
    repo          TEXT NOT NULL,           -- supports multi-repo wikis
    path          TEXT NOT NULL,           -- 'wiki/entities/nexus-api.md'
    title         TEXT NOT NULL,
    category      TEXT NOT NULL,           -- 'entity', 'concept', 'synthesis'
    tags          TEXT[] DEFAULT '{}',     -- ARRAY['security', 'api']
    summary       TEXT,                    -- one-paragraph description
    sources       TEXT[] DEFAULT '{}',     -- source doc paths
    source_count  INTEGER DEFAULT 0,
    last_ingested DATE,
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW(),
    UNIQUE(repo, path)
);

-- Cross-references between pages
CREATE TABLE wiki_links (
    id          SERIAL PRIMARY KEY,
    source_repo TEXT NOT NULL,
    source_path TEXT NOT NULL,
    target_repo TEXT NOT NULL,
    target_path TEXT NOT NULL,
    link_type   TEXT DEFAULT 'reference',  -- 'reference', 'contradicts', 'extends'
    UNIQUE(source_repo, source_path, target_repo, target_path)
);

-- Structured activity log
CREATE TABLE wiki_activity (
    id             SERIAL PRIMARY KEY,
    repo           TEXT NOT NULL,
    action         TEXT NOT NULL,          -- 'ingest', 'query', 'lint'
    target         TEXT,
    summary        TEXT,
    pages_created  INTEGER DEFAULT 0,
    pages_updated  INTEGER DEFAULT 0,
    created_at     TIMESTAMP DEFAULT NOW()
);
```

**Helper views:**
- `wiki_page_summary` — compact page listing for agent orientation
- `wiki_orphans` — pages with no inbound links (lint targets)
- `wiki_hubs` — most-linked pages (knowledge centers)

**MCP access:** Configure a `wiki-db` MCP server pointing to `postgresql://mcp_reader@localhost:5432/wiki` so your agent can query the database as a native tool.

## Page conventions

Every wiki page uses YAML frontmatter:

```yaml
---
title: "Page Title"
date: 2026-05-31
category: entity | concept | synthesis
tags:
  - relevant-tag
  - another-tag
sources:
  - "[[docs/architecture/api_setup]]"
  - "[[docs/security/threat_model]]"
last_ingested: 2026-05-31
---
```

- **Cross-references**: Use `[[wikilinks]]` for links within `wiki/`. Use standard markdown links for references to `docs/` or `raw/`.
- **Naming**: All wiki filenames use `kebab-case.md` (no date prefixes for entity/concept pages).
- **Summaries**: First paragraph after frontmatter should be a standalone summary — this gets extracted into the database.

## Operations

### Ingest

You drop a new source into `raw/` (or point the agent at a doc in `docs/`) and tell the agent to process it:

1. **Read** the source document fully
2. **Discuss** key takeaways with you
3. **Identify** entities and concepts
4. **Create** new wiki pages or **update** existing ones — noting where new data confirms, extends, or contradicts existing content
5. **Update** `wiki/index.md` with any new entries
6. **Append** to `wiki/log.md`:
   ```markdown
   ## [2026-05-31] ingest | Source Title
   - Source: `docs/architecture/api_setup.md`
   - Created: [[new-entity]]
   - Updated: [[existing-concept-1]], [[existing-concept-2]]
   - Key insight: One-line summary of what this source added
   ```
7. **Update the database** — upsert page metadata and cross-references
8. **Log activity** in the database

A single source typically touches 5-15 wiki pages. Ingest one at a time and stay involved — read the summaries, check the updates, guide the agent on what to emphasize. You can also batch-ingest with less supervision for large backlogs.

### Query

You ask questions against the wiki:

1. **Query the database** to find relevant pages:
   ```sql
   SELECT path, title, summary FROM wiki_pages
   WHERE repo = 'your-repo'
     AND (title ILIKE '%keyword%' OR 'tag' = ANY(tags));
   ```
2. **Read** the relevant wiki pages (synthesized knowledge, not raw sources)
3. **Synthesize** an answer with citations
4. If the answer is substantial: **offer to file it** as `wiki/synthesis/answer-topic.md`
5. **Log** the query in `wiki/log.md` and the database

The important insight: **good answers should be filed back into the wiki.** A comparison you asked for, an analysis, a connection you discovered — these are valuable and shouldn't disappear into chat history. Your explorations compound in the knowledge base just like ingested sources do.

### Lint

Periodically health-check the wiki:

1. **Orphan pages**: `SELECT * FROM wiki_orphans;` — pages with no inbound links
2. **Contradictions**: Flag claims in one page that contradict another
3. **Stale content**: Pages whose source documents have changed since last ingest
4. **Missing pages**: Entities or concepts frequently mentioned but lacking their own page
5. **Missing cross-references**: Pages discussing the same topic but not linking to each other
6. **Drift check** (optional): If using a drift registry, verify wiki pages against source doc dependency hashes
7. **Report** findings and suggest fixes
8. **Log** the lint in `wiki/log.md` and the database

## Session integration

If your project uses session start/wrapup workflows, the wiki integrates naturally:

**Session start:**
- Read `wiki/overview.md` to establish project context before setting goals
- The agent gets a pre-compiled understanding of the project state in one file

**Session wrapup:**
- After generating a session retrospective, ingest it into the wiki (if the session was significant — architectural changes, new features, security work)
- Skip wiki ingest for routine bug-fix or chore sessions
- Update the database with any new/modified pages

This creates a self-reinforcing loop: every significant engineering session enriches the wiki automatically.

## Drift registry integration (optional)

If your project uses a drift registry (dependency tracking between files), add a `wiki.json` registry:

```json
{
  "source_file": "wiki/entities/nexus-api.md",
  "verified_commit": "abc123",
  "dependencies": [
    {
      "type": "synthesized-from",
      "path": "docs/architecture/api_setup.md",
      "reason": "Wiki entity synthesized from this architecture doc. Re-ingest if source changes."
    }
  ]
}
```

The drift enforcer then automatically catches when a source doc changes and the wiki page built from it is stale — the staleness chain propagates: `code changes → doc stale → wiki stale → flagged for re-ingest`.

## Guardrails

- **Never modify files in `docs/`** — that's the human-authored source layer
- **Never modify files in `raw/`** — those are immutable external sources
- **Always update `index.md`** when creating or deleting wiki pages
- **Always update the database** when creating, updating, or deleting wiki pages
- **Always append to `log.md`** for every ingest, query, or lint operation
- **Flag contradictions explicitly** — don't silently overwrite one claim with another
- **Cite sources** — every claim in a wiki page should trace back to a document in `docs/` or `raw/`

## Bootstrap instructions

To set up the wiki in a new project, tell your Antigravity agent:

> **"Bootstrap the LLM Wiki for this project. Follow the wiki setup in this file: [path to this file]. Create the directory structure, initialize the database schema, configure Obsidian, and add the Wiki Maintenance Protocol to GEMINI.md."**

The agent should:
1. Create `wiki/`, `raw/`, and their subdirectories in the target project
2. Create `wiki/index.md`, `wiki/log.md`, and `wiki/overview.md`
3. Run `wiki_db_init.py` (either locally or from your infra repo) to create/verify the database schema
4. Run `wiki_db_backfill.py` to index the new project's wiki pages
5. Deploy `.obsidian/` configuration for graph colors, wikilinks, and attachment paths
6. Add the Wiki Maintenance Protocol to `GEMINI.md`
7. Configure the `wiki-db` MCP server in your Antigravity MCP config

> **Note:** For multi-repo setups, the DB scripts operate on a shared Postgres database, tracking each project via the `repo` column. You can specify a custom database connection using the `--host`, `--port`, `--user`, and `--database` flags on both scripts.

## Scaling

This architecture scales from personal use to enterprise:

| Scale | Pages | What changes |
|-------|-------|-------------|
| **Personal** | <500 | Nothing — local Postgres handles it |
| **Team** | 500–2K | Move Postgres to cloud, add `pgvector` for semantic search |
| **Department** | 2K–10K | Add domain-specialist subagents for parallel queries |
| **Enterprise** | 10K+ | Multi-agent router + specialist architecture, event-driven ingest |

The database schema is the same at every scale. What changes is where it runs and who queries it.

## Tips and tricks

- **Obsidian Web Clipper** — browser extension that converts web articles to markdown. Clip to `raw/articles/` for instant ingestion.
- **Obsidian's graph view** — the best way to see wiki shape. Color entities, concepts, and synthesis differently.
- **Dataview plugin** — runs queries over YAML frontmatter. Generate dynamic tables of pages by tag, date, or source count.
- **Download images locally** — set Obsidian's attachment folder to `raw/assets/`. Bind a hotkey to "Download attachments for current file."
- **Git versioning** — the wiki is just markdown files. You get version history, branching, and collaboration for free.
- **Selective retrospective ingest** — don't bulk-ingest every session retro. Ingest the ones that represent architectural shifts, not routine debugging sessions.

## Why this beats RAG

| | RAG | LLM Wiki + DB |
|---|---|---|
| **Knowledge accumulation** | None — re-derived every query | Persistent, compounding |
| **Cross-referencing** | Hope the retriever finds connections | Pre-compiled in `wiki_links` |
| **Contradiction detection** | Impossible — chunks are independent | Built into lint workflow |
| **Human readability** | Chunks are gibberish out of context | Complete, navigable documents |
| **Agent efficiency** | Reads 50 chunks per question | Reads 3-5 synthesized pages |
| **Context window usage** | Wastes tokens on navigation | DB query finds pages in milliseconds |
| **Maintenance burden** | Zero (but quality degrades) | Near-zero (agent does the bookkeeping) |

## Attribution

The LLM Wiki concept is by [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). This implementation adds: Postgres metadata indexing, Antigravity agent workflows, drift registry integration, session lifecycle hooks, multi-repo support, and a concrete bootstrap process. The core insight — that compiling knowledge once beats re-deriving it on every query — is entirely his.
