---
name: project-bootstrapper
description: Master orchestrator workflow ([/bootstrap-project]) to analyze task prompts, select domain archetypes and agent flavors (Antigravity or GitHub Copilot), coordinate all scaffolder sub-skills, verify 9-layer compliance, and initialize local git baseline.
---

# Project Bootstrapper (Master Orchestrator)

> **Domain:** System Bootstrapping & Workspace Provisioning  
> **Trigger:** `[/bootstrap-project]` or *"Bootstrap a new project at `<path>`"*  
> **Purpose:** Coordinate the end-to-end generation of an Obsidian + Cadence Goal Engine + Wiki Database workspace tailored to the project's domain requirements, task prompt, and target agent flavor (Personal Antigravity or Enterprise GitHub Copilot).

---

## 1. Multi-Flavor Architecture

The bootstrapper supports three agent deployment flavors:

1. **`antigravity` (Personal / Default):**
   - Emits `AGENTS.md`, `GEMINI.md`, and `.agents/skills/`.
   - Uses Google Cloud Firestore (`general-477613`) for Cadence.
   - Uses local PostgreSQL (`localhost:5432/wiki`) for wiki indexing.

2. **`copilot` (Enterprise / Work):**
   - Emits `.github/copilot-instructions.md` and `.github/prompts/` (native Copilot Chat prompt files: `session-start` and `session-wrapup`).
   - Uses **Local SQLite (`.cadence/cadence.db`)** for Cadence (zero GCP credentials, zero network dependencies).
   - Uses **Local SQLite (`.wiki/wiki.db`)** for wiki indexing (zero PostgreSQL daemon needed).
   - 100% compliant with enterprise data isolation policies.

3. **`universal` (Dual Support):**
   - Generates both Antigravity configurations (`AGENTS.md`, `.agents/`) and Copilot configurations (`.github/copilot-instructions.md`, `.github/prompts/`).

---

## 2. Interactive Consultation & Workflow

When invoked with `[/bootstrap-project]` or a prompt to bootstrap:

### Stage 1: Interactive Alignment
Ask or confirm:
1. **Target Directory & Name**: Filesystem path and project name.
2. **Environment Flavor**: Personal Antigravity (`antigravity`), Work / Enterprise Copilot (`copilot`), or Dual (`universal`).
3. **Task Prompt / Purpose**: What will the project build or manage?
4. **Archetype Selection**:
   - `software_engineering`: Full-stack apps, APIs, microservices.
   - `agentic_os`: Multi-agent systems, LLM runtimes, tool sandboxing.
   - `creative_operations`: Media archives, DAM, post-production (DaVinci/Lightroom).
   - `data_platform`: Data processing pipelines, schemas, analytics.
   - `minimal_research`: Literature vaults, academic synthesis.

### Stage 2: Scaffolding Execution
Execute the master orchestrator CLI `bootstrap.py`:

```bash
python3 ~/.gemini/config/plugins/project-bootstrap/skills/project-bootstrapper/bootstrap.py \
  --name "Project Name" \
  --target-dir "/path/to/project" \
  --archetype software_engineering \
  --flavor copilot \
  --cadence-backend sqlite \
  --wiki-backend sqlite \
  --task-prompt "<task description>" \
  --verbose
```

### Stage 3: Verification & Certification
The orchestrator automatically runs `python3 scripts/verify_bootstrap.py --verbose` asserting all 9 layers:
- Layer 1: Directory Structure (Mode 0755)
- Layer 2: Obsidian Vault Configuration
- Layer 3: Markdown Templates Frontmatter
- Layer 4: Domain Contracts & Invariants
- Layer 5: Knowledge Base & Wiki Index
- Layer 6: Database Sync & Zero Orphan Invariant (SQLite or Postgres)
- Layer 7: Wiki Export Pipeline (`wiki_bundle.json`)
- Layer 8: Cadence Goal Engine (SQLite or Firestore)
- Layer 9: Automated Test Suite & Drift Enforcer
