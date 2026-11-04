#!/usr/bin/env python3
"""
Wiki Database Schema — Creates the wiki metadata index in Postgres.

This script creates the wiki_pages, wiki_links, and wiki_activity tables
that power the database-backed wiki index. Run once to initialize.

Usage:
    python3 scripts/wiki_db_init.py [--database wiki] [--host localhost] [--port 5432]
"""

import argparse
import subprocess
import sys


SCHEMA_SQL = """
-- Wiki Database Schema v1.0
-- Metadata index for the LLM Wiki knowledge base

-- Drop existing tables if reinitializing
DROP TABLE IF EXISTS wiki_activity CASCADE;
DROP TABLE IF EXISTS wiki_links CASCADE;
DROP TABLE IF EXISTS wiki_pages CASCADE;

-- Core page registry: every wiki .md file gets a row
CREATE TABLE wiki_pages (
    id            SERIAL PRIMARY KEY,
    repo          TEXT NOT NULL,            -- e.g., 'project-repo-1', 'project-repo-2'
    path          TEXT NOT NULL,            -- 'wiki/entities/nexus-api.md'
    title         TEXT NOT NULL,            -- 'Nexus API'
    category      TEXT NOT NULL,            -- 'entity', 'concept', 'synthesis', 'index', 'log', 'overview'
    tags          TEXT[] DEFAULT '{}',      -- ARRAY['security', 'api', 'firestore']
    summary       TEXT,                     -- One-paragraph description of what this page covers
    sources       TEXT[] DEFAULT '{}',      -- Source doc paths: ARRAY['docs/architecture/api_setup.md']
    source_count  INTEGER DEFAULT 0,        -- Number of source documents referenced
    last_ingested DATE,                     -- Last time this page was updated via ingest
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW(),
    UNIQUE(repo, path)
);

-- Cross-references between wiki pages (within and across repos)
CREATE TABLE wiki_links (
    id          SERIAL PRIMARY KEY,
    source_repo TEXT NOT NULL,
    source_path TEXT NOT NULL,              -- page that contains the link
    target_repo TEXT NOT NULL,
    target_path TEXT NOT NULL,              -- page being linked to
    link_type   TEXT DEFAULT 'reference',   -- 'reference', 'contradicts', 'extends', 'supersedes'
    context     TEXT,                        -- sentence or phrase around the link
    created_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_repo, source_path, target_repo, target_path)
);

-- Structured activity log (mirrors wiki/log.md but queryable)
CREATE TABLE wiki_activity (
    id          SERIAL PRIMARY KEY,
    repo        TEXT NOT NULL,
    action      TEXT NOT NULL,              -- 'ingest', 'query', 'lint', 'update', 'create', 'delete'
    target      TEXT,                       -- page path or source path
    summary     TEXT,                       -- what happened
    pages_created  INTEGER DEFAULT 0,
    pages_updated  INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Indexes for common query patterns
CREATE INDEX idx_wiki_pages_repo ON wiki_pages(repo);
CREATE INDEX idx_wiki_pages_category ON wiki_pages(category);
CREATE INDEX idx_wiki_pages_tags ON wiki_pages USING GIN(tags);
CREATE INDEX idx_wiki_pages_sources ON wiki_pages USING GIN(sources);
CREATE INDEX idx_wiki_links_source ON wiki_links(source_repo, source_path);
CREATE INDEX idx_wiki_links_target ON wiki_links(target_repo, target_path);
CREATE INDEX idx_wiki_activity_repo ON wiki_activity(repo);
CREATE INDEX idx_wiki_activity_action ON wiki_activity(action);
CREATE INDEX idx_wiki_activity_created ON wiki_activity(created_at DESC);

-- Helper view: page summary for agent queries
CREATE OR REPLACE VIEW wiki_page_summary AS
SELECT
    repo,
    path,
    title,
    category,
    tags,
    summary,
    source_count,
    last_ingested,
    updated_at
FROM wiki_pages
ORDER BY repo, category, title;

-- Helper view: orphan detection (pages with no inbound links)
CREATE OR REPLACE VIEW wiki_orphans AS
SELECT p.repo, p.path, p.title, p.category
FROM wiki_pages p
LEFT JOIN wiki_links l ON l.target_repo = p.repo AND l.target_path = p.path
WHERE l.id IS NULL
  AND p.category NOT IN ('index', 'log', 'overview')
ORDER BY p.repo, p.path;

-- Helper view: most-linked pages (knowledge hubs)
CREATE OR REPLACE VIEW wiki_hubs AS
SELECT
    p.repo,
    p.path,
    p.title,
    p.category,
    COUNT(l.id) AS inbound_links
FROM wiki_pages p
LEFT JOIN wiki_links l ON l.target_repo = p.repo AND l.target_path = p.path
GROUP BY p.repo, p.path, p.title, p.category
HAVING COUNT(l.id) > 0
ORDER BY inbound_links DESC;
"""


def main():
    parser = argparse.ArgumentParser(description="Initialize the wiki database schema")
    parser.add_argument("--database", default="wiki", help="Database name (default: wiki)")
    parser.add_argument("--host", default="localhost", help="Postgres host")
    parser.add_argument("--port", default="5432", help="Postgres port")
    parser.add_argument("--user", default=None, help="Postgres user (default: current user)")
    args = parser.parse_args()

    # Create the database if it doesn't exist
    print(f"Creating database '{args.database}' if it doesn't exist...")
    create_db_cmd = ["createdb", args.database, "-h", args.host, "-p", args.port]
    if args.user:
        create_db_cmd.extend(["-U", args.user])

    result = subprocess.run(create_db_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        if "already exists" in result.stderr:
            print(f"  Database '{args.database}' already exists — proceeding.")
        else:
            print(f"  Warning: {result.stderr.strip()}")

    # Apply the schema
    print("Applying schema...")
    psql_cmd = ["psql", "-d", args.database, "-h", args.host, "-p", args.port, "-v", "ON_ERROR_STOP=1"]
    if args.user:
        psql_cmd.extend(["-U", args.user])

    result = subprocess.run(psql_cmd, input=SCHEMA_SQL, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: Schema creation failed:\n{result.stderr}")
        sys.exit(1)

    print("✅ Wiki database schema created successfully.")
    print(f"   Database: {args.database}")
    print(f"   Tables: wiki_pages, wiki_links, wiki_activity")
    print(f"   Views: wiki_page_summary, wiki_orphans, wiki_hubs")


if __name__ == "__main__":
    main()
