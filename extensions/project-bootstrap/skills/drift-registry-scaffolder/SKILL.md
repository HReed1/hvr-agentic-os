---
name: drift-registry-scaffolder
description: Scaffolds machine-readable drift registries in docs/drift_registries/ (wiki.json, cadence.json, governance.json), generates standalone scripts/drift_enforcer.py, and manages verified baseline stamping.
---

# Drift Registry Scaffolder

> **Domain:** System Drift Detection & Contract Verification  
> **Purpose:** Scaffold machine-readable dependency registries and standalone enforcement scripts that prevent silent architectural drift across code, ledgers, documentation, and agent rules.

## Registries Generated (`docs/drift_registries/`)

1. **`wiki.json`**:
   Tracks markdown concepts, entity catalogs, and synthesis pages against underlying source documents, code implementations, and database schemas.
2. **`cadence.json`**:
   Tracks `scripts/cadence.py`, Firestore collection schemas, phase vocabularies, and ritual meeting templates.
3. **`governance.json`**:
   Tracks `AGENTS.md`, `GEMINI.md`, `.agents/rules/`, verification harnesses, and unit tests.

## Script Generated (`scripts/drift_enforcer.py`)

A standalone, zero-dependency Python script:
- `python3 scripts/drift_enforcer.py`: Compares git commit SHAs for all tracked source files against `verified_commit` in each registry. Exits 0 if clean, exits 1 if drift detected.
- `python3 scripts/drift_enforcer.py --domain <name>`: Scopes verification to a single registry domain (`wiki`, `cadence`, `governance`).
- `python3 scripts/drift_enforcer.py --stamp`: Updates `verified_commit` for all entries with the latest git commit SHA and writes updated JSON files back to disk.

## Stamping Discipline Enforced

Drift stamps are **deliberate, infrequent boundary markers**:
- Only stamped at the end of a cohesive working session during `[/session-wrapup]`.
- Never stamped autonomously after single file edits.
