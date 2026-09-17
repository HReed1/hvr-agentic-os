---
title: "GitHub Copilot Project Bootstrapper"
date: 2026-09-17
category: entity
tags:
  - copilot
  - cli-extension
  - project-bootstrap
  - cadence
  - cross-platform
  - sqlite
  - governance
sources:
  - "[[extensions/project-bootstrap/extension.mjs]]"
  - "[[extensions/project-bootstrap/install.ps1]]"
  - "[[extensions/project-bootstrap/install.sh]]"
  - "[[extensions/project-bootstrap/README.md]]"
last_ingested: 2026-09-17
---

The **GitHub Copilot Project Bootstrapper** is a user-level extension located at `extensions/project-bootstrap/` that bridges the HvR Informatics scaffolding engine, the [[agentic-os]] governance constitution, and local SQLite goal tracking directly into GitHub Copilot CLI.

It is designed for zero-cloud enterprise portability, allowing developers to use Antigravity-grade project bootstrapping, [[drift-enforcer]] checks, and [[session-lifecycle]] rituals on corporate workstations without requiring external cloud accounts or administrative privileges.

## Architecture

```
~/.copilot/extensions/project-bootstrap/
                    │
            (Junction / Symlink)
                    │
                    ▼
hvr-agentic-os/extensions/project-bootstrap/
├── extension.mjs          # Node.js ESM bridge to Copilot CLI via @github/copilot-sdk
├── install.ps1            # Windows PowerShell installer (NTFS Junctions)
├── install.sh             # macOS/Linux symlink installer
└── skills/                # Scaffolding sub-skills & templates
    └── project-bootstrapper/
        └── bootstrap.py   # 9-Layer Master Orchestrator CLI
```

## Core Tools Registered

1. `bootstrap_project`: Orchestrates complete workspace scaffolding (Obsidian vault, SQLite Cadence, SQLite Wiki DB, `.github/copilot-instructions.md`, prompt templates, and 9-layer verification).
2. `cadence_cli`: Directly interfaces with local SQLite `.cadence/cadence.db` to list, create, advance, and synchronize daily and weekly sprint goals.
3. `drift_check`: Executes `scripts/drift_enforcer.py` against `docs/drift_registries/` to verify symbol-level AST and commit baselines.
4. `sync_wiki`: Re-exports markdown pages and updates the local SQLite database (`.wiki/wiki.db`).
5. `verify_workspace`: Runs `scripts/verify_bootstrap.py` asserting all 9 layers of workspace integrity.

## Lifecycle Hooks & Enterprise Safety

- **Session Grounding (`onSessionStart`)**: When Copilot CLI starts in any workspace containing `.cadence/cadence.db`, the extension extracts active sprint goals and automatically injects them into the agent's context notes.
- **Git Firewall (`onPreToolUse`)**: Prevents unauthorized modifications to corporate repositories by intercepting bash, powershell, or command execution tools that attempt `git push` or `gh pr merge/close/delete` commands without explicit confirmation.

## Cross-Platform Design

- **Windows Support**: Uses `python` binary detection and **NTFS Directory Junctions** via `install.ps1`, enabling standard unprivileged enterprise users to install without Administrator rights or Developer Mode.
- **Unix Support**: Uses `python3` binary detection and symbolic links via `install.sh`.
- **Zero Cloud Leakage**: Uses built-in Python `sqlite3` and auto-resolved `@github/copilot-sdk/extension` without needing npm packages or external network calls.
