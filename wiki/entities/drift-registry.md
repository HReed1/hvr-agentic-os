---
title: "Drift Registry System"
date: 2026-06-02
category: entity
tags:
  - drift
  - dependencies
  - governance
  - ci-cd
sources:
  - "[[docs/retrospectives/2026-04-23_agentic_os_drift_analysis.md]]"
last_ingested: 2026-06-02
---

# Drift Registry System

The Drift Registry System tracks cross-file dependencies within the [[agentic-os]] to prevent silent contract breakage when files change. Registries live at `docs/drift_registries/*.json` and are enforced by `scripts/drift_enforcer.py`.

## How It Works

Each registry entry maps a source file to its downstream dependents with a `verified_commit` hash. When a source file changes but its dependents haven't been reviewed, the enforcer flags drift.

### Adding an Entry
1. Determine the correct domain registry (agent, infra, docs, wiki)
2. Ask: "If this file changes, what other files could break?"
3. Add a new object to the `entries` array with `verified_commit: null`
4. Run `python3 scripts/drift_enforcer.py --stamp` to initialize

### Running the Enforcer
- **End of every session** — before committing, check for drift
- **Before merging PRs** — ensure no contracts have silently broken
- **Periodically** — as a hygiene check

## Stamping Rules

Stamping happens **only** during the session wrapup workflow (never mid-session). Drift detected during development is expected — it confirms the enforcer is working. The wrapup workflow runs `drift_enforcer.py --stamp` as a formal step.

## Wiki Integration

The `docs/drift_registries/wiki.json` registry tracks dependencies between wiki pages and their source documents. During wiki lint operations, each page's source dependencies are verified against the registry.

## See Also

- [[agentic-os]] — The system being governed
- [[amnesia-sweep]] — A related defense mechanism against state loss
