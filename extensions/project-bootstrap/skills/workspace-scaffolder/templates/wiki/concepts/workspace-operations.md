---
title: "Workspace Operations & Domain Invariants"
date: {{date}}
category: concept
tags:
  - governance
  - architecture
  - concept
sources:
  - "[[wiki/overview.md]]"
  - "[[wiki/index.md]]"
summary: "Operating principles, storage invariants, zero-state ledger discipline, and ritual workflows."
last_ingested: {{date}}
---

# Workspace Operations & Domain Invariants

> **Concept Summary**: This document formalizes the operational principles governing interactions with physical hardware, external storage volumes, live ledgers, and database indexes.

---

## 1. Prime Directives for Storage Management

### Zero-Mutation Invariant
Observability and taxonomy are strictly virtual. When inspecting external storage volumes (`/Volumes/*`) or cloud storage (`~/Library/CloudStorage/*`), agents and automated scripts are strictly forbidden from executing destructive or reorganizing commands (`mv`, `rm`, `mkdir`, `touch`, or in-place sorting scripts). All directory categorization and asset tagging are recorded virtually in `[[ledger/drives]]` and `[[ledger/assets]]`.

### Zero-Byte-Shift & Non-Hydration Invariant
Never write temporary files, audit logs, or cache directories to target storage volumes. All logs and metadata must reside within the workspace repository.
When auditing macOS FileProvider cloud repositories (Dropbox, Google Drive, iCloud), agents must never execute commands (`file`, `du -sh`, `xxh64sum`, `md5`, `ffprobe`) that trigger on-demand hydration of dataless cloud stubs to the local boot drive.

---

## 2. Ledger Architecture & Zero-State Baseline

Live production ledgers in `ledger/` are maintained in a clean state:
- `drives.yaml`: Tracks physical media and cloud endpoints.
- `projects.yaml`: Tracks active and archived production entities.
- `assets.yaml`: Master registry of project assets and checksums.

All mock schemas and synthetic demonstration records reside exclusively in `templates/examples/` to prevent agent hallucinations during session start.

---

## 3. Knowledge Base & Database Synchronization

The local Markdown knowledge base in `wiki/` is indexed into PostgreSQL (`localhost:5432/wiki`) under `repo = '{{postgres_repo_key}}'`. Cross-references must use `[[wikilinks]]`. All pages must have reciprocal links to ensure 0 orphans.
