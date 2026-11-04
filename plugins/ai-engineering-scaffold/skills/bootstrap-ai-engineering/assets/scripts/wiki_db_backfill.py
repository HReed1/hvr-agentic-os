#!/usr/bin/env python3
"""
Wiki Database Backfill — Reads existing wiki/*.md files and populates the database.

Parses YAML frontmatter to extract title, category, tags, sources, and last_ingested.
Extracts the first paragraph as the summary. Detects [[wikilinks]] as cross-references.

Usage:
    python3 scripts/wiki_db_backfill.py --repo my-project-repo --wiki-dir /path/to/my-project/wiki
    python3 scripts/wiki_db_backfill.py --repo my-project-repo --wiki-dir /path/to/my-project/wiki --dry-run
    python3 scripts/wiki_db_backfill.py --repo my-project-repo --wiki-dir /path/to/my-project/wiki --host localhost --port 5432 --user postgres
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    fm = {}
    if not content.startswith("---"):
        return fm

    end = content.find("---", 3)
    if end == -1:
        return fm

    yaml_block = content[3:end].strip()
    current_key = None
    current_list = None

    for line in yaml_block.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # List item
        if stripped.startswith("- "):
            if current_key and current_list is not None:
                val = stripped[2:].strip().strip('"').strip("'")
                current_list.append(val)
            continue

        # Key: value
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")

            if not val:
                # Start of a list
                current_key = key
                current_list = []
                fm[key] = current_list
            else:
                fm[key] = val
                current_key = key
                current_list = None

    return fm


def extract_summary(content: str) -> str:
    """Extract first non-heading, non-frontmatter paragraph as summary."""
    # Strip frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:].strip()

    lines = content.split("\n")
    paragraph_lines = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_paragraph:
                break
            continue
        if stripped.startswith("#"):
            if in_paragraph:
                break
            continue
        if stripped.startswith(">"):
            # Blockquote — could be a good summary
            paragraph_lines.append(stripped.lstrip("> ").strip())
            in_paragraph = True
            continue
        if stripped.startswith("```") or stripped.startswith("|"):
            if in_paragraph:
                break
            continue

        paragraph_lines.append(stripped)
        in_paragraph = True

    summary = " ".join(paragraph_lines)
    # Truncate to ~500 chars
    if len(summary) > 500:
        summary = summary[:497] + "..."
    return summary


def extract_wikilinks(content: str) -> list:
    """Extract [[wikilink]] targets from content.

    Fenced code blocks and inline `code spans` are ignored: a wikilink written
    as code (e.g. documenting a removed link) is literal text, not a reference.
    """
    prose = re.sub(r"^```.*?^```", "", content, flags=re.DOTALL | re.MULTILINE)
    prose = re.sub(r"`[^`\n]*`", "", prose)
    return re.findall(r'\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]', prose)


def build_page_index(md_files: list, wiki_path: Path) -> dict:
    """Map each wiki page's slug (filename stem) to its repo-relative path.

    Pages live in subdirectories (wiki/entities/, wiki/concepts/, ...), but
    wikilinks reference them by bare slug (e.g. [[agentic-os]]). If two pages
    share a slug, the first in sorted path order wins and a warning is printed.
    """
    index: dict = {}
    for md_file in sorted(md_files):
        rel_path = str(md_file.relative_to(wiki_path.parent).as_posix())
        slug = md_file.stem
        if slug in index:
            print(f"WARNING: duplicate wiki slug '{slug}': {index[slug]} and {rel_path} "
                  f"(links resolve to {index[slug]})")
            continue
        index[slug] = rel_path
    return index


def resolve_wikilink(
    link: str, page_index: dict, wiki_root: str = "wiki", repo_root: Path = None
) -> str:
    """Resolve a [[wikilink]] target to a repo-relative path.

    - `[[slug]]` / `[[slug#Heading]]` / `[[slug.md]]` -> the page with that slug in
      any wiki subdirectory (e.g. wiki/entities/slug.md).
    - `[[entities/slug]]` -> wiki/entities/slug.md (path relative to the wiki root).
    - `[[README.md]]` / `[[GEMINI]]` -> a repo-root file of that name, if it exists
      (checked only when `repo_root` is given and no wiki page matches).
    - `[[docs/...]]`, `[[wiki/...]]`, or any other repo path -> kept as-is.
    Unresolvable bare slugs fall back to `<wiki_root>/<slug>.md`.
    """
    target = link.strip().split("#", 1)[0].strip()
    if not target:
        return target
    known_paths = set(page_index.values())

    if "/" not in target:
        slug = target[:-3] if target.endswith(".md") else target
        if slug in page_index:
            return page_index[slug]
        if repo_root is not None:
            for candidate in (target, f"{slug}.md"):
                if (repo_root / candidate).is_file():
                    return candidate
        return f"{wiki_root}/{slug}.md"

    if target.startswith(f"{wiki_root}/"):
        with_ext = target if target.endswith(".md") else f"{target}.md"
        return with_ext if with_ext in known_paths else target

    # Path relative to the wiki root, e.g. [[entities/agentic-os]]
    rel_candidate = f"{wiki_root}/{target}"
    rel_candidate = rel_candidate if rel_candidate.endswith(".md") else f"{rel_candidate}.md"
    if rel_candidate in known_paths:
        return rel_candidate

    return target  # docs/... or another repo path


def sql_escape(val: str) -> str:
    """Escape single quotes for SQL."""
    if val is None:
        return "NULL"
    return "'" + val.replace("'", "''") + "'"


def sql_array(items: list) -> str:
    """Convert a Python list to a Postgres ARRAY literal."""
    if not items:
        return "ARRAY[]::TEXT[]"
    escaped = [item.replace("'", "''") for item in items]
    return "ARRAY[" + ", ".join(f"'{e}'" for e in escaped) + "]"


def main():
    parser = argparse.ArgumentParser(description="Backfill wiki database from markdown files")
    parser.add_argument("--repo", required=True, help="Repository name (e.g., my-project-repo)")
    parser.add_argument("--wiki-dir", required=True, help="Path to wiki/ directory")
    parser.add_argument("--database", default="wiki", help="Database name (default: wiki)")
    parser.add_argument("--host", default="localhost", help="Postgres host")
    parser.add_argument("--port", default="5432", help="Postgres port")
    parser.add_argument("--user", default=None, help="Postgres user (default: current user)")
    parser.add_argument("--dry-run", action="store_true", help="Print SQL without executing")
    args = parser.parse_args()

    wiki_path = Path(args.wiki_dir)
    if not wiki_path.exists():
        print(f"ERROR: Wiki directory not found: {wiki_path}")
        sys.exit(1)

    md_files = sorted(wiki_path.rglob("*.md"))
    if not md_files:
        print(f"No .md files found in {wiki_path}")
        sys.exit(0)

    print(f"Found {len(md_files)} wiki pages in {wiki_path}")

    page_index = build_page_index(md_files, wiki_path)
    wiki_root = wiki_path.resolve().name
    repo_root = wiki_path.resolve().parent

    page_inserts = []
    link_inserts = []

    for md_file in md_files:
        rel_path = str(md_file.relative_to(wiki_path.parent))  # e.g., wiki/entities/nexus-api.md
        content = md_file.read_text(encoding="utf-8", errors="replace")

        fm = parse_frontmatter(content)
        title = fm.get("title", md_file.stem.replace("-", " ").title())
        category = fm.get("category", "unknown")
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        sources = fm.get("sources", [])
        if isinstance(sources, str):
            sources = [sources]
        # Clean wikilink syntax from sources
        sources = [s.strip("[]\"' ") for s in sources]
        last_ingested = fm.get("last_ingested", fm.get("date", None))
        summary = extract_summary(content)

        page_sql = (
            f"INSERT INTO wiki_pages (repo, path, title, category, tags, summary, sources, source_count, last_ingested) "
            f"VALUES ({sql_escape(args.repo)}, {sql_escape(rel_path)}, {sql_escape(title)}, "
            f"{sql_escape(category)}, {sql_array(tags)}, {sql_escape(summary)}, "
            f"{sql_array(sources)}, {len(sources)}, "
            f"{'DATE ' + sql_escape(last_ingested) if last_ingested else 'NULL'}) "
            f"ON CONFLICT (repo, path) DO UPDATE SET "
            f"title = EXCLUDED.title, category = EXCLUDED.category, tags = EXCLUDED.tags, "
            f"summary = EXCLUDED.summary, sources = EXCLUDED.sources, source_count = EXCLUDED.source_count, "
            f"last_ingested = EXCLUDED.last_ingested, updated_at = NOW();"
        )
        page_inserts.append(page_sql)

        # Extract wikilinks as cross-references
        links = extract_wikilinks(content)
        for link in links:
            target_path = resolve_wikilink(link, page_index, wiki_root, repo_root)
            if not target_path:
                continue

            link_sql = (
                f"INSERT INTO wiki_links (source_repo, source_path, target_repo, target_path) "
                f"VALUES ({sql_escape(args.repo)}, {sql_escape(rel_path)}, "
                f"{sql_escape(args.repo)}, {sql_escape(target_path)}) "
                f"ON CONFLICT DO NOTHING;"
            )
            link_inserts.append(link_sql)

    # Activity log entry
    activity_sql = (
        f"INSERT INTO wiki_activity (repo, action, target, summary, pages_created, pages_updated) "
        f"VALUES ({sql_escape(args.repo)}, 'backfill', 'wiki/', "
        f"'Backfilled {len(page_inserts)} pages and {len(link_inserts)} links from existing wiki markdown files', "
        f"{len(page_inserts)}, 0);"
    )

    # Full backfill: replace this repo's links (stale/mis-resolved rows from earlier
    # runs would otherwise persist), atomically, scoped to this repo only.
    reset_links_sql = f"DELETE FROM wiki_links WHERE source_repo = {sql_escape(args.repo)};"
    all_sql = "\n".join(
        ["BEGIN;", reset_links_sql] + page_inserts + link_inserts + [activity_sql, "COMMIT;"]
    )

    if args.dry_run:
        print("\n--- DRY RUN: SQL that would be executed ---")
        print(all_sql)
        print(f"\n--- Summary ---")
        print(f"  Pages: {len(page_inserts)}")
        print(f"  Links: {len(link_inserts)}")
        return

    # Execute
    psql_cmd = ["psql", "-d", args.database, "-v", "ON_ERROR_STOP=1"]
    if args.host:
        psql_cmd.extend(["-h", args.host])
    if args.port:
        psql_cmd.extend(["-p", args.port])
    if args.user:
        psql_cmd.extend(["-U", args.user])

    result = subprocess.run(
        psql_cmd,
        input=all_sql,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"ERROR: Backfill failed:\n{result.stderr}")
        sys.exit(1)

    print(f"✅ Backfill complete:")
    print(f"   Pages indexed: {len(page_inserts)}")
    print(f"   Links recorded: {len(link_inserts)}")
    print(f"   Activity logged: 1 entry")


if __name__ == "__main__":
    main()
