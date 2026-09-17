---
name: workspace-scaffolder
description: Scaffolds Obsidian-compatible vault directory trees (mode 0755), BOM-free configuration JSONs, markdown templates, clean zero-state ledgers, and quarantined example fixtures tailored to specific archetypes.
---

# Workspace Scaffolder

> **Domain:** Vault Architecture & Filesystem Provisioning  
> **Purpose:** Establishes clean directory structures, Obsidian vault settings, archetype-specific markdown templates, and clean zero-state ledgers.

## Directory Archetypes Provisioned

1. **`agentic_os`**:
   - Trees: `agents/`, `core/`, `tools/`, `evals/`, `tests/`, `docs/`, `scripts/`, `wiki/` (with `entities/`, `concepts/`, `synthesis/`, `retro/`).
   - Templates: `_template_agent.md`, `_template_tool.md`, `_template_eval.md`, `_template_retro.md`.

2. **`software_engineering`**:
   - Trees: `src/`, `api/`, `tests/`, `docs/`, `scripts/`, `wiki/` (with `entities/`, `concepts/`, `synthesis/`, `retro/`).
   - Templates: `_template_feature.md`, `_template_architecture_decision.md`, `_template_retro.md`.

3. **`creative_operations`**:
   - Trees: `ledger/` (with `attachments/`), `projects/`, `meetings/`, `scripts/`, `wiki/` (with `entities/`, `concepts/`, `synthesis/`, `retro/`).
   - Templates: `_template_project.md`, `_template_asset.md`, `_template_drive_audit.md`, `_template_meeting.md`, `_template_retro.md`.
   - Ledgers: Zero-state production catalogs in `ledger/` (`drives.yaml`, `projects.yaml`, `assets.yaml`) and mock fixtures quarantined in `templates/examples/`.

4. **`data_platform`**:
   - Trees: `pipelines/`, `data/`, `schemas/`, `notebooks/`, `tests/`, `docs/`, `scripts/`, `wiki/`.
   - Templates: `_template_pipeline.md`, `_template_schema.md`, `_template_retro.md`.

5. **`minimal_research`**:
   - Trees: `papers/`, `notes/`, `drafts/`, `scripts/`, `wiki/`.
   - Templates: `_template_paper.md`, `_template_experiment.md`, `_template_retro.md`.

## Universal Components

- **Mode 0755:** All directories created with explicit permissions.
- **Obsidian Configuration:** Installs BOM-free configuration files in `.obsidian/`:
  - `app.json`, `appearance.json`, `graph.json`, `editor.json`, `templates.json`, `core-plugins.json`.
- **Core Wiki Pages:** `wiki/overview.md`, `wiki/index.md`, `wiki/log.md`, `wiki/concepts/workspace-operations.md`.
