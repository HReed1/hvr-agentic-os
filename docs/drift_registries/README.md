# Drift Registries

Machine-readable JSON files that track cross-file dependencies in the `hvr-agentic-os` codebase.

## Purpose

LLM agents don't accumulate institutional memory between sessions. These registries encode the implicit contracts between files — "if this file changes, these other files need to be checked" — so drift is caught before it causes bugs, security holes, or documentation rot.

## Registries

| Registry | Domain | What it tracks |
|----------|--------|----------------|
| `agent.json` | Agent governance | Agent rules, skills, and workflows ↔ the source files they govern |
| `infra.json` | Infrastructure | Dockerfiles ↔ requirements ↔ CI configs ↔ build scripts |
| `docs.json` | Documentation | Docs ↔ the source code they describe |

## Usage

```bash
# Check all domains for drift (exit code 1 if drift detected)
python3 scripts/drift_enforcer.py

# Check a specific domain
python3 scripts/drift_enforcer.py --domain agent

# After reviewing flagged items, stamp current hashes
python3 scripts/drift_enforcer.py --stamp

# Report coverage: what percentage of repo files are tracked
python3 scripts/drift_enforcer.py --coverage
```

## Schema

See [docs/reference/drift-registry.md](../reference/drift-registry.md) for the full specification.

## Stamping Rules

> **IMPORTANT**: Only stamp at session end, never mid-session. Drift detected during development is expected — it means the enforcer is working. Save stamping for the wrapup step.
