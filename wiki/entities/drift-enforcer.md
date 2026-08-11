---
title: "Drift Enforcer"
date: 2026-08-11
category: entity
tags:
  - drift-detection
  - infrastructure
  - git
  - dependency-tracking
  - enforcement
sources:
  - "[[scripts/drift_enforcer.py]]"
  - "[[.agents/skills/drift-registry/SKILL.md]]"
  - "[[.agents/rules/drift-detection-governance.md]]"
  - "[[docs/retrospectives/2026-08-11_wiki_db_infrastructure_and_v2_wiki_expansion.md]]"
last_ingested: 2026-08-11
---

The Drift Enforcer is the Python script at `scripts/drift_enforcer.py` that enforces architectural dependency contracts across the [[agentic-os]] codebase. It compares each tracked file's `verified_commit` hash against its current git HEAD hash, surfacing silent contract breakage before it causes bugs, security holes, or documentation rot. The enforcer is the executable heart of the [[drift-registry]] system and a core component of **v2.0.0 Pillar 2: Git-Hash Drift Registry**.

## How It Works

The enforcer auto-discovers registries via a `docs/drift_registries/*.json` glob pattern. Each registry JSON contains entries mapping a `source_file` to a `verified_commit` SHA and an array of downstream `dependencies`. For each entry, the enforcer runs `git log --format=%H -1 -- <filepath>` to get the current commit hash, then compares it against the stored `verified_commit`.

Every entry is classified into one of four states:

| Symbol | State | Meaning |
|--------|-------|---------|
| ✅ | **Clean** | `verified_commit` matches current HEAD — no drift |
| ⚠️ | **Drifted** | Source file changed since last verification — all dependencies need review |
| ❓ | **Unstamped** | Entry has `verified_commit: null` — run `--stamp` to initialize |
| ❌ | **Missing** | Source file no longer exists on disk — remove or update the entry |

## Domain Registries

The enforcer operates across four domain registries, each tracking a different architectural layer:

| Registry | Domain | What It Tracks |
|----------|--------|----------------|
| `agent.json` | Agent governance | GEMINI.md, agent rules, workflows, skills ↔ source files they govern |
| `docs.json` | Documentation | Docs ↔ source code and systems they describe |
| `infra.json` | Infrastructure | Dockerfiles ↔ requirements ↔ CI configs ↔ build scripts |
| `wiki.json` | Wiki system | Wiki pages ↔ source documents they were synthesized from |

## Dependency Types

Registry entries use typed dependencies to express the nature of the contract between files:

| Type | Registry | Meaning |
|------|----------|---------|
| `rule` | `agent.json` | Source defines a behavioral constraint → agent rule must enforce it |
| `skill` | `agent.json` | Source exposes a capability → skill definition must match its interface |
| `workflow` | `agent.json` | Source defines a process → workflow must implement described steps |
| `describes` | `docs.json` | Documentation describes source → doc must reflect current implementation |
| `manifest` | `infra.json` | Package manifest ↔ consumer (Dockerfile, CI) |
| `build` | `infra.json` | Build script references target → path/tag changes break build |
| `config` | `infra.json` | Config file consumed by another process → changes must propagate |
| `entrypoint` | `infra.json` | Entry script that CI/build invokes → must exist and resolve |
| `synthesized-from` | `wiki.json` | Wiki page synthesized from source doc → content must stay current |

## CLI Interface

```bash
# Check all domains (exit code 1 if drift detected)
python3 scripts/drift_enforcer.py

# Check a specific domain only
python3 scripts/drift_enforcer.py --domain agent

# Stamp current git hashes into all registries
python3 scripts/drift_enforcer.py --stamp

# Report what percentage of repo files are tracked
python3 scripts/drift_enforcer.py --coverage
```

The `--coverage` flag computes the ratio of registry-tracked files to total git-tracked files, excluding binary assets (`.png`, `.svg`, `.jpg`, etc.), lock files, and the `public/` directory. It lists the top untracked files to guide coverage expansion.

## Stamping Discipline

> **CRITICAL:** Stamping is ONLY allowed at session-wrapup boundaries — never mid-session.

Drift detected during active development is **expected and healthy** — it means the enforcer is working. Premature stamping hides real drift by silently blessing uncommitted or unreviewed changes. The stamping ceremony is a formal step in the session-wrapup workflow:

1. Run `python3 scripts/drift_enforcer.py` to check all domains
2. Review every flagged entry and diff the source files
3. Update dependent files if the change affects the documented contract
4. Run `python3 scripts/drift_enforcer.py --stamp` to write current hashes
5. Commit the updated registry JSON alongside the code changes

This discipline is enforced by the [[zero-trust-auditor]] as part of session governance.

## Staleness Propagation

The enforcer enables transitive staleness detection. When a source document changes, its wiki page (tracked via `synthesized-from` in `wiki.json`) is flagged as stale. This creates a propagation chain: `code changes → doc entry drifted → wiki page stale → flagged for re-ingest`. The [[drift-registry]] and the [[agentic-os]] session lifecycle work together to ensure these chains are resolved before stamping.

## Integration Points

- **[[drift-registry]]** — the enforcer is the executable component; the registry is the data layer
- **[[agentic-os]]** — drift checks are mandatory at session wrapup (Step 2 of `/session-wrapup`)
- **[[zero-trust-auditor]]** — audits stamping discipline and coverage accountability
- **Wiki system** — `wiki.json` registry tracks wiki page ↔ source doc dependencies for the [[llm-wiki]]
