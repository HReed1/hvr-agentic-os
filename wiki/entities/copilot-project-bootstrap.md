---
title: "GitHub Copilot Project Bootstrapper (Superseded)"
date: 2026-09-17
category: entity
status: superseded
superseded_by: "[[ai-engineering-scaffold]]"
tags:
  - copilot
  - cli-extension
  - project-bootstrap
  - superseded
sources:
  - "[[docs/retrospectives/2026-11-04_harness_agnostic_scaffold_and_plugin.md]]"
last_ingested: 2026-11-04
---

# GitHub Copilot Project Bootstrapper (Superseded)

> [!WARNING]
> **Superseded on 2026-11-04 by [[ai-engineering-scaffold]].** The `extensions/project-bootstrap/` directory was removed from the repository.

## What It Was

A user-level GitHub Copilot CLI extension (`extensions/project-bootstrap/`, ingested 2026-09-17) that wrapped a template-driven `bootstrap.py` orchestrator: it generated a 9-layer workspace (Obsidian vault, local SQLite Cadence goal engine, SQLite wiki DB, archetype governance) and exposed `bootstrap_project`, `cadence_cli`, `drift_check`, `sync_wiki`, and `verify_workspace` tools plus a git-guardrail hook. It was installed via `install.sh` / `install.ps1` (NTFS junctions) into `~/.copilot/extensions/project-bootstrap`.

## Why It Was Retired

It diverged from the canonical [[agentic-os]] scaffold. `bin/bootstrap_ai_engineering.sh` is the canonical approach: a thin skeleton plus an LLM ingest prompt that has the agent implement the reference guides, rather than pre-rendered templates. The replacement plugin (`plugins/ai-engineering-scaffold/`) packages that script for Antigravity, Claude Code, Codex, and Copilot. Its Copilot CLI extension keeps the `drift_check` tool and the git-guardrail hook, and adds a `bootstrap_ai_engineering` tool. Related: [[drift-enforcer]], [[session-lifecycle]].
