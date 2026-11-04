"""Tests for wikilink resolution in scripts/wiki_db_backfill.py.

Regression: bare-slug wikilinks ([[agentic-os]]) used to resolve to
`wiki/agentic-os.md`, ignoring the entities/ and concepts/ subdirectories, so no
link ever matched a real page and every page appeared in `wiki_orphans`.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "wiki_db_backfill.py"

_spec = importlib.util.spec_from_file_location("wiki_db_backfill", SCRIPT)
backfill = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(backfill)


def make_wiki(root: Path) -> Path:
    wiki = root / "wiki"
    (wiki / "entities").mkdir(parents=True)
    (wiki / "concepts").mkdir()
    (wiki / "index.md").write_text("---\ntitle: Index\ncategory: index\n---\n[[agentic-os]] [[token-tax]]\n")
    (wiki / "entities" / "agentic-os.md").write_text(
        "---\ntitle: Agentic OS\ncategory: entity\n---\nSee [[token-tax|the tax]] and [[entities/drift-enforcer#How]].\n"
    )
    (wiki / "entities" / "drift-enforcer.md").write_text(
        "---\ntitle: Drift Enforcer\ncategory: entity\n---\nPart of [[agentic-os]]. Source [[docs/reference/drift-registry.md]].\n"
    )
    (wiki / "concepts" / "token-tax.md").write_text(
        "---\ntitle: Token Tax\ncategory: concept\n---\nRelated: [[agentic-os.md]], [[missing-page]].\n"
    )
    return wiki


def test_resolves_bare_slugs_into_subdirectories(tmp_path: Path) -> None:
    wiki = make_wiki(tmp_path)
    index = backfill.build_page_index(sorted(wiki.rglob("*.md")), wiki)
    r = lambda link: backfill.resolve_wikilink(link, index, "wiki")  # noqa: E731

    assert r("agentic-os") == "wiki/entities/agentic-os.md"
    assert r("token-tax") == "wiki/concepts/token-tax.md"
    assert r("agentic-os.md") == "wiki/entities/agentic-os.md"
    assert r("drift-enforcer#How It Works") == "wiki/entities/drift-enforcer.md"
    assert r("entities/drift-enforcer") == "wiki/entities/drift-enforcer.md"
    assert r("wiki/concepts/token-tax") == "wiki/concepts/token-tax.md"
    assert r("docs/reference/drift-registry.md") == "docs/reference/drift-registry.md"
    assert r("bin/bootstrap_ai_engineering.sh") == "bin/bootstrap_ai_engineering.sh"
    assert r("missing-page") == "wiki/missing-page.md"  # unresolved fallback


def test_bare_links_to_repo_root_files(tmp_path: Path) -> None:
    wiki = make_wiki(tmp_path)
    (tmp_path / "README.md").write_text("# readme")
    (tmp_path / "GEMINI.md").write_text("# gemini")
    index = backfill.build_page_index(sorted(wiki.rglob("*.md")), wiki)
    r = lambda link: backfill.resolve_wikilink(link, index, "wiki", tmp_path)  # noqa: E731
    assert r("README.md") == "README.md"
    assert r("GEMINI") == "GEMINI.md"
    assert r("agentic-os") == "wiki/entities/agentic-os.md"  # wiki pages still win
    assert r("missing-page") == "wiki/missing-page.md"


def test_extract_wikilinks_ignores_code() -> None:
    content = (
        "Real: [[agentic-os]] and [[token-tax|alias]].\n"
        "Literal: `[[development-workflow]]` was removed.\n"
        "```markdown\n[[inside-fence]]\n```\n"
        "After fence: [[drift-enforcer]]\n"
    )
    assert backfill.extract_wikilinks(content) == ["agentic-os", "token-tax", "drift-enforcer"]


def test_duplicate_slugs_resolve_deterministically(tmp_path: Path, capsys) -> None:
    wiki = tmp_path / "wiki"
    (wiki / "concepts").mkdir(parents=True)
    (wiki / "entities").mkdir()
    (wiki / "concepts" / "dup.md").write_text("x")
    (wiki / "entities" / "dup.md").write_text("y")
    index = backfill.build_page_index(list(wiki.rglob("*.md")), wiki)
    assert index["dup"] == "wiki/concepts/dup.md"
    assert "duplicate wiki slug 'dup'" in capsys.readouterr().out


def test_dry_run_emits_resolved_links_and_atomic_repo_scoped_reset(tmp_path: Path) -> None:
    wiki = make_wiki(tmp_path)
    res = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", "demo", "--wiki-dir", str(wiki), "--dry-run"],
        capture_output=True,
        text=True,
        check=True,
    )
    sql = res.stdout
    assert "BEGIN;\nDELETE FROM wiki_links WHERE source_repo = 'demo';" in sql
    assert "\nCOMMIT;\n" in sql
    assert "'wiki/entities/agentic-os.md', 'demo', 'wiki/concepts/token-tax.md'" in sql
    assert "'wiki/concepts/token-tax.md', 'demo', 'wiki/entities/agentic-os.md'" in sql
    assert "'wiki/entities/agentic-os.md', 'demo', 'wiki/entities/drift-enforcer.md'" in sql
    assert "'demo', 'wiki/agentic-os.md'" not in sql  # the old mis-resolution
