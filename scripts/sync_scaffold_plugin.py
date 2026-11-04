#!/usr/bin/env python3
"""Sync the AI Engineering scaffold plugin from its canonical sources.

The canonical scaffold is `bin/bootstrap_ai_engineering.sh` plus the four
reference guides in `docs/reference/` and the helper scripts in `scripts/`.
`plugins/ai-engineering-scaffold/` is only a distribution vehicle: its
`skills/bootstrap-ai-engineering/assets/` directory holds byte-identical copies
of those canonical files so the plugin works when installed outside this repo.

Never edit files under `assets/` directly — edit the canonical file, then run:

    python3 scripts/sync_scaffold_plugin.py          # copy canonical -> plugin
    python3 scripts/sync_scaffold_plugin.py --check  # exit 1 if out of sync (CI/tests)
"""

from __future__ import annotations

import argparse
import filecmp
import os
from pathlib import Path
import shutil
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "plugins" / "ai-engineering-scaffold"
ASSETS_DIR = PLUGIN_ROOT / "skills" / "bootstrap-ai-engineering" / "assets"

# Canonical files bundled into the plugin, as repo-relative paths. The same
# relative layout is preserved under ASSETS_DIR so the bootstrap script can
# locate its resources via `$SCRIPT_DIR/..` in both locations.
CANONICAL_FILES = (
    "bin/bootstrap_ai_engineering.sh",
    "docs/reference/llm-wiki-antigravity.md",
    "docs/reference/drift-registry.md",
    "docs/reference/session-workflows.md",
    "docs/reference/elephant-goldfish-verification.md",
    "scripts/drift_enforcer.py",
    "scripts/wiki_db_init.py",
    "scripts/wiki_db_backfill.py",
)


def find_problems() -> list[str]:
    """Return a list of human-readable sync problems (empty if in sync)."""
    problems: list[str] = []
    for rel in CANONICAL_FILES:
        src, dst = REPO_ROOT / rel, ASSETS_DIR / rel
        if not src.is_file():
            problems.append(f"canonical file missing: {rel}")
        elif not dst.is_file():
            problems.append(f"plugin copy missing: {dst.relative_to(REPO_ROOT)}")
        elif not filecmp.cmp(src, dst, shallow=False):
            problems.append(f"plugin copy out of date: {dst.relative_to(REPO_ROOT)}")
    expected = {ASSETS_DIR / rel for rel in CANONICAL_FILES}
    if ASSETS_DIR.is_dir():
        for path in ASSETS_DIR.rglob("*"):
            if path.is_file() and path not in expected:
                problems.append(f"unexpected file in plugin assets: {path.relative_to(REPO_ROOT)}")
    return problems


def sync() -> int:
    """Copy every canonical file into the plugin assets; prune strays."""
    for rel in CANONICAL_FILES:
        src, dst = REPO_ROOT / rel, ASSETS_DIR / rel
        if not src.is_file():
            print(f"Error: canonical file missing: {rel}", file=sys.stderr)
            return 1
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if os.access(src, os.X_OK):
            dst.chmod(dst.stat().st_mode | 0o111)
        print(f"  synced {rel}")
    expected = {ASSETS_DIR / rel for rel in CANONICAL_FILES}
    for path in sorted(ASSETS_DIR.rglob("*"), reverse=True):
        if path.is_file() and path not in expected:
            path.unlink()
            print(f"  removed stray {path.relative_to(REPO_ROOT)}")
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check", action="store_true", help="Verify sync without writing (exit 1 on drift)."
    )
    args = parser.parse_args()

    if args.check:
        problems = find_problems()
        if problems:
            print("AI Engineering scaffold plugin is OUT OF SYNC:")
            for p in problems:
                print(f"  - {p}")
            print("Run: python3 scripts/sync_scaffold_plugin.py")
            return 1
        print(f"Plugin in sync ({len(CANONICAL_FILES)} canonical files).")
        return 0

    print(f"Syncing canonical scaffold files into {ASSETS_DIR.relative_to(REPO_ROOT)}/ ...")
    return sync()


if __name__ == "__main__":
    sys.exit(main())
