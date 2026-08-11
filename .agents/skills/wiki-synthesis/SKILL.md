---
name: wiki-synthesis
description: Synthesizes wiki entity and concept pages from source documents (retrospectives, decisions, guides, director context), maintains the wiki database via psql, and enforces wiki quality standards.
---

# Wiki Synthesis

## Purpose

The wiki is a living knowledge base for `hvr-agentic-os`. Unlike raw source documents (retrospectives, decisions, guides), wiki pages present **synthesized, cross-referenced, queryable knowledge** — entities (things that exist) and concepts (ideas that recur).

Source documents live in `docs/retrospectives/`, `docs/decisions/`, `docs/guides/`, and `docs/director_context/`. Wiki pages live in `wiki/entities/`, `wiki/concepts/`, and `wiki/synthesis/`. The wiki database is a Postgres `wiki` database on `localhost:5432`.

---

## When To Activate This Skill (Auto-Trigger Conditions)

Activate this skill whenever:

1. **A new retrospective, decision, guide, or director context document is created** — it likely contains entities or concepts that should be extracted into wiki pages
2. **An existing source document is significantly updated** — downstream wiki pages may need revision
3. **A user asks a question whose answer spans multiple documents** — synthesize a wiki page to capture the cross-cutting answer
4. **The drift enforcer flags stale `wiki.json` entries** — source documents changed but wiki pages weren't updated
5. **A session wrapup identifies new architectural patterns or anti-patterns** — they should be captured as concept pages
6. **A new agent, tool, or subsystem is introduced** — it needs an entity page

Do **NOT** activate for:
- Trivial edits to source docs (typo fixes, formatting changes)
- Files outside the source document directories
- Changes to code files without architectural significance

---

## Workflow

### Step 1 — Identify Source Material

Scan the relevant source document(s) for extractable knowledge:

| Source Directory | Typical Content |
|-----------------|----------------|
| `docs/retrospectives/` | Architectural evolution, benchmarks, failure analyses, era transitions |
| `docs/decisions/` | Design decisions, implementation plans, methodology definitions |
| `docs/guides/` | How-to walkthroughs, benchmark execution, evaluation procedures |
| `docs/director_context/` | Swarm architecture specs, API boundaries, system topology |

### Step 2 — Classify Wiki Page Type

| Type | Directory | What It Describes | Examples |
|------|-----------|-------------------|----------|
| **Entity** | `wiki/entities/` | A concrete thing that exists in the system | `director-agent.md`, `staging-airlock.md`, `drift-registry.md` |
| **Concept** | `wiki/concepts/` | An abstract idea or pattern that recurs | `tdaid-methodology.md`, `token-tax.md`, `amnesia-sweep.md` |
| **Synthesis** | `wiki/synthesis/` | A cross-cutting analysis joining multiple entities/concepts | _(none yet — created on demand)_ |

### Step 3 — Write the Wiki Page

Every wiki page **must** include YAML frontmatter:

```yaml
---
title: "Page Title"
date: 2026-08-10
category: entity          # entity | concept | synthesis
tags:
  - relevant-tag-1
  - relevant-tag-2
sources:
  - "[[docs/retrospectives/2026-04-23_example.md]]"
  - "[[docs/decisions/2026-04-23_example.md]]"
last_ingested: 2026-08-10
---
```

#### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `title` | ✅ | Human-readable title, in quotes |
| `date` | ✅ | ISO date of creation or last major revision |
| `category` | ✅ | One of: `entity`, `concept`, `synthesis`, `index`, `log` |
| `tags` | ✅ | Array of lowercase kebab-case tags for discoverability |
| `sources` | ✅ | Array of `[[wikilink]]` paths to source documents |
| `last_ingested` | ✅ | ISO date when source material was last ingested into this page |

#### Content Structure

Follow this structure for entity and concept pages:

```markdown
# Page Title

> One-sentence summary of what this is.

## What It Is / How It Works
[Core explanation — 2-4 paragraphs]

## Key Details
[Specifics, constraints, configuration, metrics]

## See Also
- [[related-entity]] — Brief reason for the cross-reference
- [[related-concept]] — Brief reason for the cross-reference
```

#### Wikilinks

Use `[[page-slug]]` (no directory prefix, no `.md` extension) for cross-references between wiki pages:
- ✅ `[[tdaid-methodology]]`
- ❌ `[[wiki/concepts/tdaid-methodology.md]]`
- ❌ `[[TDAID Methodology]]`

### Step 4 — Update the Wiki Index

Add the new page to `wiki/index.md` in the appropriate table (Entities, Concepts, or Synthesis):

```markdown
| [[new-page-slug]] | Brief summary | N |
```

Where `N` is the number of source documents cited in the page's `sources` frontmatter.

### Step 5 — Update the Wiki Log

Append a log entry to `wiki/log.md`:

```markdown
## [YYYY-MM-DD] ingest | Brief Description
- Sources ingested:
  - `docs/retrospectives/example.md`
- Created: [[new-page-slug]] — Brief summary
- Updated: [[existing-page]] — What changed
- Key insight: One sentence on the most important takeaway
```

### Step 6 — Sync to the Wiki Database

The wiki database is a Postgres database. The wiki-db MCP server is **READ-ONLY** — all writes must use `psql` directly.

#### For new pages — run the backfill script:

```bash
python3 scripts/wiki_db_backfill.py --repo hvr-agentic-os --wiki-dir wiki
```

This parses all `wiki/**/*.md` files, extracts YAML frontmatter, detects `[[wikilinks]]`, and upserts into the database.

#### For targeted updates — use psql directly:

```bash
# Insert a new page
psql -h localhost -p 5432 -d wiki -c "
INSERT INTO pages (repo, slug, title, category, body, tags, sources, last_ingested)
VALUES (
  'hvr-agentic-os',
  'new-page-slug',
  'Page Title',
  'entity',
  'Full markdown body...',
  ARRAY['tag1','tag2'],
  ARRAY['docs/retrospectives/example.md'],
  '2026-08-10'
)
ON CONFLICT (repo, slug) DO UPDATE SET
  title = EXCLUDED.title,
  body = EXCLUDED.body,
  tags = EXCLUDED.tags,
  sources = EXCLUDED.sources,
  last_ingested = EXCLUDED.last_ingested;
"

# Insert cross-references
psql -h localhost -p 5432 -d wiki -c "
INSERT INTO xrefs (repo, from_slug, to_slug)
VALUES ('hvr-agentic-os', 'new-page-slug', 'related-page')
ON CONFLICT DO NOTHING;
"
```

#### For querying (read-only) — use the wiki-db MCP tool:

The `wiki-db` MCP server supports read queries for searching pages, checking for existing content, and validating cross-references before writing.

---

## Quality Checklist

Before committing any wiki changes, verify:

- [ ] **Frontmatter complete** — All 6 required fields present with correct types
- [ ] **Sources cited** — Every factual claim traces to a source document in `sources`
- [ ] **No orphan wikilinks** — Every `[[link]]` resolves to an existing page, or create the missing page
- [ ] **No contradictions** — New content doesn't conflict with existing wiki pages (check overlapping entities/concepts)
- [ ] **Index updated** — New pages appear in `wiki/index.md`
- [ ] **Log updated** — Operation recorded in `wiki/log.md`
- [ ] **Database synced** — Backfill script run or psql commands executed
- [ ] **Drift registry** — If this wiki page has source dependencies, add an entry to `docs/drift_registries/wiki.json` with `synthesized-from` type

---

## Wiki Lint Operations

Periodically (and at session wrapup), run a wiki lint pass:

1. **Orphan check** — Find wiki pages not linked from `index.md` or any other page
2. **Broken wikilink check** — Find `[[links]]` that don't resolve to existing pages
3. **Contradiction check** — Scan for conflicting claims across pages (e.g., agent X is described differently in two entity pages)
4. **Staleness check** — Compare `last_ingested` dates against source document modification dates
5. **Source coverage** — Identify source documents in `docs/` not referenced by any wiki page

Record lint results in the wiki log, including any auto-fixes applied.

---

## Current Wiki State

The wiki currently contains:

### Entities (12 pages)

| Page | Summary |
|------|---------|
| `agentic-os` | The Zero-Trust Multi-Agent OS itself |
| `director-agent` | Top-level orchestration node |
| `executor-agent` | Code mutation engine |
| `qa-engineer-agent` | Adversarial test gate |
| `zero-trust-auditor` | Final deployment gate |
| `staging-airlock` | The `.staging/` sandbox |
| `zero-trust-interceptors` | Signal routing and loop termination |
| `dlp-proxy` | PHI/HIPAA redaction layer |
| `evaluation-framework` | Automated benchmarking infrastructure |
| `telemetry-engine` | Trace extraction and reporting |
| `seqera-ai-integration` | Nextflow/nf-core cross-agent integration |
| `drift-registry` | Cross-file dependency tracking |

### Concepts (10 pages)

| Page | Summary |
|------|---------|
| `tdaid-methodology` | Test-Driven AI Development protocol |
| `token-tax` | Context bloat from shared conversations |
| `context-caching` | Static/dynamic instruction split (56% token reduction) |
| `amnesia-sweep` | `git clean -fd` defense protocol |
| `tool-parallelism-bottleneck` | Irreducible ~4× multi-agent overhead |
| `solo-vs-swarm-benchmarks` | Empirical Solo vs Swarm comparison |
| `hierarchical-routing` | SequentialAgent tree architecture |
| `anti-pattern-knowledge-graph` | Documented systemic failure modes |
| `ephemeral-memory-handoff` | Cross-session persistence |
| `empirical-verification` | No-assumptions debugging methodology |

### Synthesis (0 pages)

No synthesis pages yet. These are created on demand when cross-cutting analysis is needed.

---

## Common Mistakes

### ❌ Writing wiki pages without YAML frontmatter
Every wiki page must have the 6-field frontmatter block. The backfill script and database sync depend on it. Pages without frontmatter are invisible to the database.

### ❌ Using the wiki-db MCP tool for writes
The wiki-db MCP server is **READ-ONLY**. All database writes must use `psql -h localhost -p 5432 -d wiki -c "..."` or the backfill script. Attempting MCP writes will silently fail.

### ❌ Forgetting to update the index and log
Wiki pages not listed in `wiki/index.md` become invisible to agents searching for knowledge. Log entries not written to `wiki/log.md` break the audit trail.

### ❌ Copying source documents verbatim
Wiki pages are **synthesized** — they distill, cross-reference, and contextualize. Don't paste a retrospective into a wiki page. Extract the entities, concepts, and relationships, then write a fresh synthesis.

### ❌ Creating duplicate entity pages
Before creating a new entity page, check if the entity is already covered. Use the wiki-db MCP tool to search:
```
Query: SELECT slug, title FROM pages WHERE repo = 'hvr-agentic-os' AND category = 'entity';
```

### ❌ Omitting `sources` from frontmatter
Every wiki page must cite its sources. Unsourced claims can't be verified or updated when source material changes. The drift registry depends on source traceability.

### ❌ Using full paths in wikilinks
Wikilinks use slugs only: `[[tdaid-methodology]]`, not `[[wiki/concepts/tdaid-methodology.md]]`. The slug is the filename without the `.md` extension.

### ❌ Skipping the database sync
Wiki pages on disk but not in the database can't be queried by agents using the wiki-db MCP tool. Always run the backfill script or execute psql inserts after creating or updating pages.

### ❌ Not adding wiki.json drift entries
When synthesizing a wiki page from source documents, add a `synthesized-from` entry in `docs/drift_registries/wiki.json`. Without this, the drift enforcer can't detect when source documents change and wiki pages become stale.
