---
title: "{{project_name}} — Living Project Synthesis"
date: {{date}}
category: overview
tags:
  - synthesis
  - architecture
  - overview
sources:
  - "[[wiki/index.md]]"
  - "[[wiki/concepts/workspace-operations.md]]"
summary: "High-level architectural overview, current state, active pipelines, and operating invariants."
last_ingested: {{date}}
---

# {{project_name}} — Living Project Synthesis

> **Executive Synthesis**: Real-time snapshot of system state, storage topology, active goals, and operational invariants for {{project_name}}.

---

## 1. Project Mission & Scope
Executive mission statement and strategic objectives for {{project_name}}.

---

## 2. Operating Invariants
1. **Zero-Mutation Invariant**: All physical media and raw cloud storage repositories are strictly read-only. Media reorganization and taxonomy are handled entirely via virtual ledgers.
2. **Zero-Byte-Shift & Non-Hydration Invariant**: Never write temporary files, audit scratch files, or logs to target external volumes. Never force-download dataless cloud stubs on macOS FileProvider.
3. **Database Scoping & Multi-Tenancy**: All knowledge graph operations in PostgreSQL are strictly partitioned by `repo = '{{postgres_repo_key}}'`.
4. **Cadence Goal Scoping**: All Cadence tasks and sprint goals in Firestore are scoped to `{{firestore_collection}}`.

---

## 3. Storage & Systems Architecture
- Master ledgers: `[[ledger/drives]]`, `[[ledger/projects]]`, `[[ledger/assets]]`.
- Knowledge base: Local Obsidian vault synced to PostgreSQL (`localhost:5432/wiki`).
- Engineering cadence: Firestore 3-tier goal hierarchy (`scripts/cadence.py`).
