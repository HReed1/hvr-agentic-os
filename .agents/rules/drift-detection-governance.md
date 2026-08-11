---
description: "Rules for when to invoke drift detection to track architectural dependencies across the hvr-agentic-os ecosystem."
---

# Drift Detection & Registry Governance

You are operating within the hvr-agentic-os ecosystem, which strictly enforces architectural boundaries and dependency tracking via a series of machine-readable drift registries located in `docs/drift_registries/`.

## Active Registries

| Registry | Domain | Tracks |
|----------|--------|--------|
| `agent.json` | Agent layer | GEMINI.md, agent rules, workflows, skills, swarm architecture |
| `docs.json` | Documentation | Retrospectives, ADRs, wiki pages, README cross-references |
| `infra.json` | Infrastructure | Dockerfiles, requirements, CI/CD configs, deploy scripts |
| `wiki.json` | Wiki system | Wiki pages, backfill script, wiki-db MCP server contracts |

## Mandatory Invocation Triggers

You **MUST** run the drift enforcer (`python3 scripts/drift_enforcer.py`) whenever ANY of the following occur during your session:

1. **A new source file is created** that depends on or is depended upon by existing files (e.g., adding a new MCP server, a new agent rule, a new workflow, or a utility script that references existing code).

2. **A new dependency relationship is discovered** (e.g., debugging reveals a workflow depends on a script name, or a new governance rule references a specific MCP tool or swarm agent definition).

3. **An existing file gains a new consumer** (e.g., a new workflow starts using an existing skill, a new evaluation test references agent prompts, or a new wiki page cross-references existing entities).

4. **At session wrapup**, when the drift report or `git diff` reveals files created or modified during the session that are not tracked in any drift registry. This is enforced by Step 2 of the `/session-wrapup` workflow.

If you detect any of these conditions while generating code, modifying architecture, or debugging, your **mandatory first step** is to register the new relationship in the appropriate domain registry (`docs/drift_registries/<domain>.json`) before concluding your work.

## Coverage Accountability

Running `python3 scripts/drift_enforcer.py` and cross-referencing the session's changed files against registry tracking is a **mandatory step before stamping** at session boundaries. Stamping drift registries without evaluating coverage is a governance violation — it allows new source files to slip through untracked and defeats the purpose of the drift system.

You can also run `python3 scripts/drift_enforcer.py --coverage` for a broader view of what percentage of repo files are tracked and which important files are missing.

## What to Track

Focus tracking effort on the **most important and connected files**:

- **Governance boundaries:** `GEMINI.md` ↔ `.agents/rules/*.md`
- **Agent definitions:** `.agents/agents.md` ↔ agent prompts ↔ swarm architecture
- **MCP server contracts:** MCP server definitions ↔ skill docs ↔ workflow references
- **Infrastructure configurations:** `Dockerfile` ↔ `requirements.txt` ↔ CI/CD YAML
- **Wiki system:** `wiki/` pages ↔ `scripts/wiki_db_backfill.py` ↔ wiki-db MCP server

Not every file needs a registry entry, but files with cross-file dependencies **must** be tracked.

## Stamping Discipline

> [!CAUTION]
> **Never stamp during active development.** Drift detected mid-session is expected — it means the enforcer is working correctly. Stamping is reserved exclusively for the session-wrapup workflow (Step 2 of `/session-wrapup`). Premature stamping masks genuine drift and undermines the entire safety net.

To stamp when authorized:

```bash
python3 scripts/drift_enforcer.py --stamp
```

## Registry Entry Format

Each entry in a domain registry follows this structure:

```json
{
  "source_file": "path/to/tracked/file.py",
  "verified_commit": "<sha>",
  "dependencies": [
    {
      "type": "rule|workflow|skill|script|config|doc",
      "path": "path/to/dependency",
      "reason": "Why this dependency exists and what breaks if they diverge."
    }
  ]
}
```

When adding entries, always include a `reason` that explains the *architectural coupling* — not just that files are related, but what specifically breaks if they diverge.
