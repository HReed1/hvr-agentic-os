---
name: wiki-db-scaffolder
description: Scaffolds the multi-tenant PostgreSQL wiki synchronization pipeline (scripts/export_wiki.py, scripts/sync_wiki_db.py) with repo-level isolation and orphan assertions.
---

# Wiki-DB Scaffolder

> **Domain:** Multi-Tenant Knowledge Persistence & Database Indexing  
> **Purpose:** Generate the two-step wiki compilation and database synchronization pipeline (`scripts/export_wiki.py` and `scripts/sync_wiki_db.py`), ensuring strict multi-tenant isolation in `localhost:5432/wiki`.

## Pipeline Architecture

```text
wiki/ (*.md) + docs/ (*.md)
       │
       ▼ [scripts/export_wiki.py]
  wiki_bundle.json (AST-parsed frontmatter, tags, summaries, wikilinks)
       │
       ▼ [scripts/sync_wiki_db.py]
PostgreSQL Database (localhost:5432/wiki)
  - wiki_pages (scoped to repo = '<project_slug>')
  - wiki_links (inbound and outbound wikilinks)
  - wiki_activity (structured audit log)
  - wiki_orphans (view asserting 0 orphan pages)
```

## Guardrails Enforced

1. **Self-Contained Implementation**: Zero dependencies on external project modules. Runs directly with standard Python 3.11+ plus `pyyaml` and `psycopg2-binary`.
2. **Resilient User Resolution**: Falls back safely across `WIKI_DB_USER` -> `USER` -> `harrisonreed` -> `postgres`.
3. **Multi-Tenant Partitioning**: All records and deletions are strictly filtered by `repo = '<project_slug>'`. Sibling project records (`wonder`, `hvr-informatics`, `hvr-agentic-os`) are completely untouched.
4. **Zero Orphan Invariant**: Asserts that all pages have at least one inbound cross-reference or source citation.
