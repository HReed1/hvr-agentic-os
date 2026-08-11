---
description: "Syncs wiki markdown files from the filesystem into the Postgres wiki database, verifies page counts, and logs the activity."
---

# Wiki Database Sync

> **Trigger:** Run when wiki pages have been created, updated, or deleted and
> the Postgres database needs to reflect those changes. Also invoked as part of
> the `/session-wrapup` workflow when wiki ingest occurred.

> [!IMPORTANT]
> The `wiki-db` MCP server is **read-only**. All database writes must go through
> `psql` directly or via the backfill script. Never attempt INSERT/UPDATE/DELETE
> through the MCP server — it will fail silently or error.

## Step 1: Run the Backfill Script

Sync all wiki markdown files from disk into the Postgres `wiki` database:

```bash
python3 scripts/wiki_db_backfill.py --repo hvr-agentic-os --wiki-dir wiki
```

**Expected output:**
```
Found N wiki pages in wiki
✅ Backfill complete:
   Pages indexed: N
   Links recorded: M
   Activity logged: 1 entry
```

If this is the first sync or you want to preview without writing, add `--dry-run`:

```bash
python3 scripts/wiki_db_backfill.py --repo hvr-agentic-os --wiki-dir wiki --dry-run
```

## Step 2: Verify Page Counts

Confirm the database page count matches the filesystem:

1. **Count files on disk:**
   ```bash
   find wiki -name '*.md' | wc -l
   ```

2. **Count rows in database** (use the wiki-db MCP server for reads):
   ```sql
   SELECT COUNT(*) AS db_pages FROM wiki_pages WHERE repo = 'hvr-agentic-os';
   ```

3. **Compare:** The two counts should match. If the database has fewer rows,
   re-run the backfill. If the database has more rows, orphaned pages exist
   (files were deleted from disk but not cleaned from the DB).

## Step 3: Check Orphans and Hub Pages

1. **Orphan pages** (zero inbound links — may be disconnected from the graph):
   ```sql
   SELECT p.path, p.title
   FROM wiki_pages p
   LEFT JOIN wiki_links l ON l.target_path = p.path AND l.target_repo = p.repo
   WHERE p.repo = 'hvr-agentic-os'
     AND l.id IS NULL
   ORDER BY p.path;
   ```

2. **Hub pages** (most outbound links — these are your most connected pages):
   ```sql
   SELECT p.path, p.title, COUNT(l.id) AS outbound_links
   FROM wiki_pages p
   JOIN wiki_links l ON l.source_path = p.path AND l.source_repo = p.repo
   WHERE p.repo = 'hvr-agentic-os'
   GROUP BY p.path, p.title
   ORDER BY outbound_links DESC
   LIMIT 10;
   ```

Review orphans — if they should be linked, update the relevant wiki pages to
include `[[wikilinks]]` and re-run the backfill.

## Step 4: Log the Sync Activity

Record this sync as a tracked activity event via `psql`:

```bash
psql -h localhost -p 5432 -d wiki -c "
INSERT INTO wiki_activity (repo, action, target, summary, pages_created, pages_updated)
VALUES ('hvr-agentic-os', 'sync', 'wiki/',
        'Wiki DB sync — <N> pages indexed, <M> links recorded',
        0, <pages_updated>);
"
```

Replace `<N>`, `<M>`, and `<pages_updated>` with the actual counts from Step 1 output.

## Step 5: Stage and Commit

If wiki pages were created or modified during this session, commit them:

```bash
git add wiki/
git commit -m "docs(wiki): sync wiki pages to database"
```

> Do not push to remote unless explicitly requested by the user.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `psql: connection refused` | Ensure Postgres is running: `pg_isready -h localhost -p 5432` |
| `ERROR: relation "wiki_pages" does not exist` | Run the init script: `python3 scripts/wiki_db_init.py` |
| Backfill reports 0 pages | Verify `wiki/` directory exists and contains `.md` files |
| Count mismatch after backfill | Check for files outside `wiki/` or files with parse errors in frontmatter |
| MCP server returns stale data | The MCP server caches queries — re-run queries after a short delay |
