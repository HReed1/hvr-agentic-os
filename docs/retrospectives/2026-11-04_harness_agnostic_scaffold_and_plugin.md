# Session Retrospective: Harness-Agnostic AI Engineering Scaffold & Plugin

> **Date:** 2026-11-04
> **Branch:** `goldfish_update`
> **Commit:** `48865b4` — feat(scaffold): harness-agnostic bootstrap_ai_engineering.sh and ai-engineering-scaffold plugin

## Context/Objective

Make the AI Engineering scaffold agnostic to the agent harness and model (Antigravity, Claude Code, Codex, GitHub Copilot), and make it easy to share as a plugin — so another person can adopt it by following the README or by installing the plugin into their harness.

## Key Accomplishments

- **Canonical script made harness-agnostic** — `bin/bootstrap_ai_engineering.sh` gained:
  - `--harness antigravity|claude|codex|copilot|all` (repeatable/comma-separated, aliases). It tailors the LLM Ingest Prompt's harness mapping: `AGENTS.md` is always the shared source of truth; `GEMINI.md` (Antigravity), `CLAUDE.md` with `@AGENTS.md` import (Claude Code), self-contained `AGENTS.md` under 32 KiB (Codex), `.github/copilot-instructions.md` (Copilot). Skills go to `.agents/skills/` (Antigravity/Codex/Copilot) or `.claude/skills/` (Claude), with per-harness Goldfish subagent spawning.
  - `--wiki-db postgres|none` (default `none`), `--db-user/--db-name/--db-host/--db-port` (user defaults to `$USER`, never a hardcoded name), `--author` (defaults to `git config user.name`), `--target-dir`.
  - Explicit "do not assume Firestore/Cadence/Jira" guard in the prompt.
  - Copies the four reference guides, `drift_enforcer.py`, and (with Postgres) `wiki_db_init.py`/`wiki_db_backfill.py` into other repos — replacing the old "copy manually" step.
  - **New vs. existing repo detection** before creating anything: existing repos get an integration-mode prompt (append to `AGENTS.md`, pointer-only edits to existing instruction files, seed the wiki from existing docs, list every pre-existing file touched); new repos ask for a project description; non-git targets get a `git init` warning.
  - Records choices in `.agents/scaffold-config.json`. Remains bash 3.2 compatible and idempotent.
- **Plugin as a distribution vehicle** — `plugins/ai-engineering-scaffold/`:
  - `skills/bootstrap-ai-engineering/SKILL.md` runs the bundled script and executes the ingest prompt itself.
  - `assets/` holds byte-identical synced copies of the canonical files; `scripts/sync_scaffold_plugin.py` (with `--check`) keeps them in sync.
  - Manifests for Antigravity (`plugin.json`) and Claude Code (`.claude-plugin/plugin.json` + repo-root `.claude-plugin/marketplace.json`); rewritten Copilot CLI extension (`copilot/extension.mjs`); `install.sh --harness …` symlink installer.
- **Retired** the outdated `extensions/project-bootstrap/` (bootstrap.py templating approach) and the locally installed `~/.gemini/config/plugins/project-bootstrap` (moved to the conversation scratch area, not deleted). Installed the new plugin for Antigravity and Copilot.
- **README** — harness/option tables, "install the plugin using your current harness" prompts, and new-repo vs. existing-repo walkthroughs.
- **Tests** — `tests/test_ai_engineering_scaffold.py` (16 tests): harness tailoring, aliases, Postgres user/author handling, JSON escaping, resource copying, idempotency, invalid args, new/existing modes, plugin sync, manifests, standalone plugin execution. Full suite: 22 passed.

## Files Modified

- `bin/bootstrap_ai_engineering.sh` (rewritten)
- `plugins/ai-engineering-scaffold/**` (new), `.claude-plugin/marketplace.json` (new)
- `scripts/sync_scaffold_plugin.py` (new), `tests/test_ai_engineering_scaffold.py` (new)
- `README.md`, `docs/drift_registries/docs.json`, `docs/drift_registries/wiki.json`
- `extensions/project-bootstrap/**` (deleted)

## Drift Report

- **`docs` domain:** three new, unstamped entries added this session — `bin/bootstrap_ai_engineering.sh` (deps: README, plugin asset copy, SKILL.md, plugin README, Copilot extension, tests), `docs/reference/elephant-goldfish-verification.md` (deps: plugin copy, script prompt step 4), `scripts/sync_scaffold_plugin.py` (deps: script resources, tests). Existing guide entries gained plugin-copy and script-consumer dependencies. All dependencies were reviewed and updated in-session (assets synced, `--check` passes, README/SKILL aligned) — safe to stamp.
- **`wiki` domain (pre-existing drift from earlier sessions):** `wiki/index.md` and `wiki/log.md` (changed by `620bfd1`, the bootstrap_plugin merge), and `wiki/entities/agentic-os.md` / `wiki/entities/session-lifecycle.md` (1–3 line edits in `a1f5d9a`, a prior wrapup commit made after its stamp). Content-only wiki edits; their consumers (backfill script, session-wrapup skill format) are unaffected — safe to stamp. `wiki/entities/copilot-project-bootstrap.md` (never stamped) described the removed extension; superseded and re-pointed during this wrapup's wiki ingest.
- **`agent` / `infra` domains:** clean.

## Decisions/Gotchas

- **Wrong bootstrap first.** The session initially extended the outdated `bootstrap.py` plugin instead of the canonical `bin/bootstrap_ai_engineering.sh`. Lesson: confirm which artifact is canonical before editing when multiple implementations of the same idea exist. That work was retired, but its findings carried over (harness file mapping, Claude's `@AGENTS.md` import, Codex's 32 KiB limit and `.agents/skills/` discovery, `codex exec --sandbox read-only --ephemeral` for Goldfish).
- **Canonical vs. distribution.** The script + `docs/reference/` stay canonical; the plugin only packages synced copies, enforced by `sync_scaffold_plugin.py --check` in `pytest tests/` and drift registry entries.
- **Guides untouched.** `docs/` is read-only per the wiki protocol, so harness translation lives in the ingest prompt rather than in the guides.
- **`.agents/workflows/` dropped** in favor of skill directories for every harness (Antigravity already migrated to skills on 2026-09-07).
- **Unverified externals.** Codex details came from search summaries of mostly third-party pages. The Claude Code marketplace install and the Copilot extension were not exercised live (no Claude Code installed locally).

## Carryover

- **Push/merge to `main`** before `/plugin marketplace add HReed1/hvr-agentic-os` works for Claude Code users.
- **Live-test** the Claude Code plugin install (and `claude plugin validate`, if available) and the Copilot CLI extension.
- **Optional:** decide whether Cadence (or another task tracker) should become a first-class `--tracker` option; it is currently opt-in by asking the agent.
- **Optional:** whether re-running on a freshly bootstrapped repo should remember "new" mode (it currently reports "existing" because the first run created `wiki/index.md`).
