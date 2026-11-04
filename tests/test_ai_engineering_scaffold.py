"""Tests for the canonical AI Engineering scaffold and its plugin packaging.

Covers `bin/bootstrap_ai_engineering.sh` (harness/DB/author handling, resource
copying, idempotency) and `plugins/ai-engineering-scaffold/` (byte-identical
sync with the canonical files, manifests, standalone execution).
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "bin" / "bootstrap_ai_engineering.sh"
PLUGIN_ROOT = REPO_ROOT / "plugins" / "ai-engineering-scaffold"
PLUGIN_SCRIPT = (
    PLUGIN_ROOT / "skills" / "bootstrap-ai-engineering" / "assets" / "bin" / "bootstrap_ai_engineering.sh"
)
GUIDES = (
    "llm-wiki-antigravity.md",
    "drift-registry.md",
    "session-workflows.md",
    "elephant-goldfish-verification.md",
)

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="bash is required")


def run_bootstrap(target: Path, *args: str, script: Path = SCRIPT) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(script), "--target-dir", str(target), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def ingest_prompt(stdout: str) -> str:
    start = stdout.index("Initialize this project's AI Engineering scaffold")
    return stdout[start : stdout.index("END OF PROMPT")]


# ── Canonical script ─────────────────────────────────────────────────────────


def test_default_harness_is_antigravity_and_db_is_none(tmp_path: Path) -> None:
    res = run_bootstrap(tmp_path / "proj")
    assert res.returncode == 0, res.stderr
    prompt = ingest_prompt(res.stdout)
    assert "Agent harness(es): Antigravity" in prompt
    assert "`GEMINI.md` (Antigravity)" in prompt
    assert "`CLAUDE.md` (Claude Code)" not in prompt
    assert "Wiki database is NONE" in prompt
    assert "Firestore" in prompt  # explicit "do not assume Firestore" guard
    assert (tmp_path / "proj" / ".agents" / "skills").is_dir()
    assert not (tmp_path / "proj" / ".claude").exists()


@pytest.mark.parametrize(
    ("harness", "expected", "absent", "skill_dirs"),
    [
        ("claude", ["`CLAUDE.md` (Claude Code): first line must be `@AGENTS.md`"], ["`GEMINI.md` (Antigravity)"], [".claude/skills"]),
        ("codex", ["stay under 32 KiB", "codex exec --sandbox read-only --ephemeral"], ["`CLAUDE.md` (Claude Code)", "`GEMINI.md` (Antigravity)"], [".agents/skills"]),
        ("copilot", ["`.github/copilot-instructions.md`"], ["`CLAUDE.md` (Claude Code)", "`GEMINI.md` (Antigravity)"], [".agents/skills"]),
    ],
)
def test_harness_tailors_prompt_and_skill_dirs(
    tmp_path: Path, harness: str, expected: list[str], absent: list[str], skill_dirs: list[str]
) -> None:
    target = tmp_path / harness
    res = run_bootstrap(target, "--harness", harness)
    assert res.returncode == 0, res.stderr
    prompt = ingest_prompt(res.stdout)
    for snippet in expected:
        assert snippet in prompt
    mapping = prompt.split("Harness mapping")[1].split("2. Skills")[0]
    for snippet in absent:
        assert snippet not in mapping
    for d in skill_dirs:
        assert (target / d).is_dir()
    config = json.loads((target / ".agents" / "scaffold-config.json").read_text())
    assert config["harnesses"] == harness


def test_multiple_harnesses_aliases_and_all(tmp_path: Path) -> None:
    res = run_bootstrap(tmp_path / "multi", "--harness", "claude-code", "--harness", "openai")
    assert res.returncode == 0, res.stderr
    config = json.loads((tmp_path / "multi" / ".agents" / "scaffold-config.json").read_text())
    assert config["harnesses"] == "claude codex"
    assert config["skill_dirs"] == ".agents/skills .claude/skills"
    assert "keep `.claude/skills/` byte-identical" in ingest_prompt(res.stdout)

    res_all = run_bootstrap(tmp_path / "all", "--harness", "all")
    assert res_all.returncode == 0, res_all.stderr
    config_all = json.loads((tmp_path / "all" / ".agents" / "scaffold-config.json").read_text())
    assert config_all["harnesses"] == "antigravity claude codex copilot"


def test_postgres_uses_selected_user_and_author(tmp_path: Path) -> None:
    target = tmp_path / "pg"
    res = run_bootstrap(
        target, "--wiki-db", "postgres", "--db-user", "alice", "--db-name", "kb", "--author", 'Jane "JD" Doe'
    )
    assert res.returncode == 0, res.stderr
    prompt = ingest_prompt(res.stdout)
    assert "--database kb --host localhost --port 5432 --user alice" in prompt
    assert "psql -h localhost -p 5432 -U alice -d kb" in prompt
    assert "harrisonreed" not in prompt
    assert 'Author: Jane "JD" Doe' in prompt
    config = json.loads((target / ".agents" / "scaffold-config.json").read_text())
    assert config["db_user"] == "alice" and config["author"] == 'Jane "JD" Doe'
    assert (target / "scripts" / "wiki_db_init.py").is_file()
    assert (target / "scripts" / "wiki_db_backfill.py").is_file()


def test_none_db_skips_db_scripts_and_records_blank_user(tmp_path: Path) -> None:
    target = tmp_path / "nodb"
    res = run_bootstrap(target, "--wiki-db", "none", "--db-user", "alice")
    assert res.returncode == 0, res.stderr
    assert not (target / "scripts" / "wiki_db_init.py").exists()
    assert json.loads((target / ".agents" / "scaffold-config.json").read_text())["db_user"] == ""


def test_copies_guides_and_enforcer_and_is_idempotent(tmp_path: Path) -> None:
    target = tmp_path / "idem"
    assert run_bootstrap(target).returncode == 0
    for guide in GUIDES:
        assert (target / "docs" / "reference" / guide).read_bytes() == (
            REPO_ROOT / "docs" / "reference" / guide
        ).read_bytes()
    assert (target / "scripts" / "drift_enforcer.py").is_file()

    (target / "wiki" / "overview.md").write_text("custom\n")
    second = run_bootstrap(target)
    assert second.returncode == 0, second.stderr
    assert (target / "wiki" / "overview.md").read_text() == "custom\n"
    assert "Skipped: wiki/overview.md already exists." in second.stdout


@pytest.mark.parametrize("args", [["--harness", "cursor"], ["--wiki-db", "sqlite"], ["--bogus"]])
def test_invalid_arguments_fail_without_side_effects(tmp_path: Path, args: list[str]) -> None:
    target = tmp_path / "bad"
    res = run_bootstrap(target, *args)
    assert res.returncode != 0
    assert "Error:" in res.stderr
    assert not target.exists()


def test_new_repo_mode_asks_for_description_and_warns_without_git(tmp_path: Path) -> None:
    target = tmp_path / "fresh"
    res = run_bootstrap(target)
    assert res.returncode == 0, res.stderr
    prompt = ingest_prompt(res.stdout)
    assert "New repository:" in prompt
    assert "Existing repository:" not in prompt
    assert "Run `git init`" in prompt
    assert "is not a git repository" in res.stdout
    assert json.loads((target / ".agents" / "scaffold-config.json").read_text())["repo_mode"] == "new"


def test_existing_repo_mode_integrates_without_overwriting(tmp_path: Path) -> None:
    target = tmp_path / "existing"
    target.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    (target / "README.md").write_text("# My App\n")
    (target / "CLAUDE.md").write_text("# House rules\nkeep me\n")

    res = run_bootstrap(target, "--harness", "claude")
    assert res.returncode == 0, res.stderr
    prompt = ingest_prompt(res.stdout)
    assert "Existing repository:" in prompt
    assert "In the existing instruction files (`CLAUDE.md`)" in prompt
    assert "Seed the wiki from what already exists" in prompt
    assert "git init" not in prompt
    assert (target / "CLAUDE.md").read_text() == "# House rules\nkeep me\n"
    assert (target / "README.md").read_text() == "# My App\n"
    assert json.loads((target / ".agents" / "scaffold-config.json").read_text())["repo_mode"] == "existing"


# ── Plugin packaging ─────────────────────────────────────────────────────────


def test_plugin_assets_are_in_sync_with_canonical_files() -> None:
    res = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "sync_scaffold_plugin.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, res.stdout


def test_plugin_manifests_are_valid() -> None:
    for manifest in (
        PLUGIN_ROOT / "plugin.json",
        PLUGIN_ROOT / ".claude-plugin" / "plugin.json",
        REPO_ROOT / ".claude-plugin" / "marketplace.json",
    ):
        data = json.loads(manifest.read_text())
        assert data["name"]
    skill = (PLUGIN_ROOT / "skills" / "bootstrap-ai-engineering" / "SKILL.md").read_text()
    assert skill.startswith("---\nname: bootstrap-ai-engineering\n")


def test_plugin_copy_runs_standalone_outside_repo(tmp_path: Path) -> None:
    installed = tmp_path / "installed-plugin"
    shutil.copytree(PLUGIN_ROOT, installed)
    script = installed / PLUGIN_SCRIPT.relative_to(PLUGIN_ROOT)
    target = tmp_path / "consumer"
    res = run_bootstrap(target, "--harness", "codex", script=script)
    assert res.returncode == 0, res.stderr
    assert sorted(p.name for p in (target / "docs" / "reference").iterdir()) == sorted(GUIDES)
    assert (target / "scripts" / "drift_enforcer.py").is_file()
