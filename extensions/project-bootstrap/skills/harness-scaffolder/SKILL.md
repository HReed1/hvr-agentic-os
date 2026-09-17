---
name: harness-scaffolder
description: Scaffolds the comprehensive 9-layer bootstrap verification harness (scripts/verify_bootstrap.py) and dual-state automated test suites in tests/ (pre_audit_uninitialized vs active_audited).
---

# Harness Scaffolder

> **Domain:** Verification & Quality Assurance  
> **Purpose:** Generate the 9-layer automated verification harness (`scripts/verify_bootstrap.py`) and dual-state unit tests (`tests/`), certifying workspace readiness before live usage.

## Verification Layers Generated

1. **Layer 1: Directory Structure**: 12+ required directories exist with exact mode `0755`.
2. **Layer 2: Obsidian Vault Configuration**: 6 JSON files exist in `.obsidian/`, valid JSON, UTF-8 BOM-free.
3. **Layer 3: Markdown Templates**: Frontmatter schema completeness and phase coverage.
4. **Layer 4: Manual Ledgers Referential Integrity**: Dual-state verification (`pre_audit_uninitialized` zero-state vs `active_audited`), primary key uniqueness, foreign key validation against quarantined fixtures in `templates/examples/`.
5. **Layer 5: Knowledge Base & Concepts**: Concept guide validation, frontmatter integrity, reciprocal cross-references.
6. **Layer 6: PostgreSQL Knowledge Index**: Validates connection fallback, `repo = '<project_slug>'` partitioning, and 0 orphans.
7. **Layer 7: Wiki Pipeline Scripts**: Verifies `export_wiki.py` and `sync_wiki_db.py` execution and bundle generation.
8. **Layer 8: Firestore Cadence Lifecycle**: Interactive subprocess test creating, listing, advancing, completing, and tearing down a temporary goal in `<project_slug>_goals`.
9. **Layer 9: Code Quality & Test Suites**: Executes unit tests via `python3 -m unittest discover tests`, verifies Black and Flake8 compliance, and validates drift registries.

## Dual-State Test Suite (`tests/`)

- `test_ledgers.py`: Evaluates schema rules against `templates/examples/` while cleanly accommodating either zero-state (`pre_audit_uninitialized`) or populated (`active_audited`) records in `ledger/`.
- `test_cadence.py`: Asserts domain phase vocabularies, scope transitions, and invalid phase rejection.
- `test_wiki.py`: Validates frontmatter, slug normalization, and bundle compilation.
