---
title: "AI Engineering Scaffold & Plugin"
date: 2026-11-04
category: entity
tags:
  - scaffold
  - bootstrap
  - plugin
  - harness-agnostic
  - antigravity
  - claude
  - codex
  - copilot
sources:
  - "[[docs/retrospectives/2026-11-04_harness_agnostic_scaffold_and_plugin.md]]"
  - "[[docs/retrospectives/2026-11-05_ai_engineering_onboarding_playbook.md]]"
  - "[[bin/bootstrap_ai_engineering.sh]]"
  - "[[plugins/ai-engineering-scaffold/README.md]]"
  - "[[README.md]]"
last_ingested: 2026-11-05
---

# AI Engineering Scaffold & Plugin

The **AI Engineering Scaffold** is the portable, harness-agnostic way to install the four pillars of this repo's engineering practice — the [[llm-wiki]], the [[drift-registry]] (checked by the [[drift-enforcer]]), the [[session-lifecycle]] rituals, and Elephant-Goldfish verification — into any repository, for any agent harness.

## Canonical Source vs. Distribution

| Layer | Location | Role |
| :--- | :--- | :--- |
| **Canonical** | `bin/bootstrap_ai_engineering.sh` + `docs/reference/*.md` (4 guides) + `scripts/drift_enforcer.py`, `wiki_db_*.py` | The single source of truth. Edit here. |
| **Distribution** | `plugins/ai-engineering-scaffold/` | Packages byte-identical synced copies under `skills/bootstrap-ai-engineering/assets/`. Never edited directly. |

`scripts/sync_scaffold_plugin.py` copies canonical → plugin; its `--check` mode runs inside `pytest tests/`, and `docs/drift_registries/docs.json` tracks the dependencies, so the plugin cannot silently fall behind.

## How the Bootstrap Works

The script is deliberately thin: it builds the skeleton (`wiki/`, `docs/drift_registries/`, `.agents/rules|personas`, skills dir), copies the reference guides and helper scripts into the target, records `.agents/scaffold-config.json`, and prints an **LLM Ingest Prompt**. The *agent* then writes the governance files by implementing the guides — tailored to the project.

- **`--harness`** (`antigravity | claude | codex | copilot | all`) selects the instruction files and skill directories in the prompt's harness mapping. `AGENTS.md` is always the shared source of truth; `GEMINI.md` (Antigravity), `CLAUDE.md` starting with `@AGENTS.md` (Claude Code), self-contained `AGENTS.md` under 32 KiB (Codex), or `.github/copilot-instructions.md` (Copilot) are added as needed. Skills land in `.agents/skills/` (read natively by Antigravity, Codex, and Copilot) or `.claude/skills/`.
- **`--wiki-db postgres|none`** (default markdown-only) with `--db-user/--db-name/--db-host/--db-port`; **`--author`**; **`--target-dir`**. No external tracker (Firestore, Cadence, Jira) is assumed.
- **New vs. existing repos** are detected before anything is created. Existing repos get an integration-mode prompt (append, never overwrite; investigate the repo alongside asking the user clarifying questions to seed an initial high-level wiki covering the main areas of the repo; list touched files). New repos get a project-description prompt and a `git init` warning when needed.
- **4-Session Onboarding Playbook (Existing Repos):** Because reading the four reference guides and creating governance files consumes a substantial portion of the bootstrap session's context window, onboarding an existing codebase is split across four clean sessions:
  1. **Session 1 (Bootstrap & High-Level Seed):** Install the scaffold, investigate existing docs/code + ask clarifying Q&A, seed `wiki/overview.md` and main-area pages, and commit.
  2. **Session 2 (Deep Wiki & Drift Registry Ingestion):** In a fresh session (`/session-start`), deeply ingest critical `wiki/entities/`, `wiki/concepts/`, and cross-file contracts in `docs/drift_registries/`.
  3. **Session 3 (Codebase Audit & Prioritization):** Audit and categorize **Current Most Critical Issues**, **Low-Hanging Fruit**, and **Long-Term Robust Optimizations & Bug Fixes** (validated with `/goldfish-review`), filing the roadmap into `wiki/synthesis/`.
  4. **Session 4+ (Feature Development):** Build features or execute roadmap items with compounding wiki and drift protection.
- The reference guides in `docs/` are never edited — harness translation lives in the ingest prompt (see [[empirical-verification]] for why claims about external harnesses are flagged as unverified until tested).

## Plugin Packaging

- **Skill:** `bootstrap-ai-engineering` confirms settings, runs the bundled script, and executes the ingest prompt itself.
- **Install:** `install.sh --harness …` symlinks into `~/.gemini/config/plugins/` (Antigravity), `~/.claude/skills/` (Claude Code — or the repo's `.claude-plugin/marketplace.json`), `~/.agents/skills/` (Codex), or `~/.copilot/extensions/` + `~/.copilot/skills/` (Copilot CLI extension).
- **Supersedes:** [[copilot-project-bootstrap]] and the template-driven `bootstrap.py` plugin (retired 2026-11-04).

## Open Items

- Claude Code marketplace install requires the plugin to be merged to `main`; neither it nor the Copilot extension has been exercised live yet.
- Task tracking (e.g. Cadence) is opt-in via the agent, not a scaffold flag.
