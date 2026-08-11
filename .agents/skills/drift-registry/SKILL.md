---
name: drift-registry
description: Manages cross-file dependency tracking via drift registries and the drift_enforcer.py script. Covers adding entries, choosing dependency types, stamping verified_commit hashes, and interpreting enforcer output.
---

# Drift Registry Management

## Purpose

The drift registry system prevents silent contract breakage across the `hvr-agentic-os` codebase. LLM agents don't carry institutional memory between sessions — these registries encode the implicit contracts between files so that drift is caught before it causes bugs, security holes, or documentation rot.

Registries live at `docs/drift_registries/*.json`. The enforcer script is `scripts/drift_enforcer.py`.

---

## When To Activate This Skill

- You are **creating or modifying** a file that has downstream dependents (rules, skills, workflows, docs, configs, scripts)
- You are **reviewing drift enforcer output** and need to interpret or resolve flagged entries
- You are asked to **add, update, or stamp** registry entries
- A **session wrapup** workflow is running and drift must be checked before commit
- You discover that a file has **implicit contracts** with other files not yet tracked

---

## The Four Domain Registries

| Registry | Domain | What It Tracks |
|----------|--------|----------------|
| `agent.json` | Agent governance | Agent rules, skills, workflows ↔ the source files they govern |
| `docs.json` | Documentation | Docs ↔ the source code and systems they describe |
| `infra.json` | Infrastructure | Dockerfiles ↔ requirements ↔ CI configs ↔ build scripts |
| `wiki.json` | Wiki knowledge base | Wiki pages ↔ source documents they were synthesized from |

### Choosing the Right Registry

- **agent.json** — The source file is an agent governance artifact (`GEMINI.md`, `.agents/agents.md`, `agent_app/*.py`, `.agents/rules/*`, `.agents/skills/*`, `.agents/workflows/*`)
- **docs.json** — The source file is a reference doc, guide, decision, retrospective, or director context document that describes code or systems
- **infra.json** — The source file is a Dockerfile, `requirements.txt`, CI workflow, build script, or infrastructure config
- **wiki.json** — The source file is a wiki page (`wiki/**/*.md`) that was synthesized from upstream source documents

---

## Registry Entry Schema

```json
{
  "source_file": "path/to/source.py",
  "verified_commit": "abc123...",
  "dependencies": [
    {
      "type": "rule",
      "path": ".agents/rules/example-rule.md",
      "reason": "Source defines constraint X — rule must enforce the same constraint."
    }
  ]
}
```

### Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `source_file` | ✅ | Repo-relative path to the canonical source file |
| `verified_commit` | ✅ | Full SHA of the last commit where this entry was verified (set to `null` for new entries) |
| `dependencies` | ✅ | Array of downstream files that must stay in sync with the source |
| `dependencies[].type` | ✅ | Dependency relationship type (see table below) |
| `dependencies[].path` | ✅ | Repo-relative path to the dependent file |
| `dependencies[].reason` | ✅ | Human-readable explanation of **why** the dependency exists and **what** could break |

### Symbol-Level Tracking

For large files with many independent contracts, you can optionally scope dependencies to specific symbols:

```json
{
  "source_file": "agent_app/agents.py",
  "verified_commit": "abc123...",
  "symbols": ["DirectorAgent", "QAEngineerAgent"],
  "dependencies": [
    {
      "type": "rule",
      "path": ".agents/rules/staging-promotion-protocol.md",
      "reason": "DirectorAgent routing defines promotion boundaries — rule must match."
    }
  ]
}
```

The `symbols` field is optional. When present, drift is only flagged if the specified symbols (classes, functions, constants) were modified — not on unrelated edits to the same file.

---

## Dependency Type Reference

| Type | Used In | Meaning |
|------|---------|---------|
| `rule` | `agent.json` | Source file defines a behavioral constraint → an agent rule must enforce it |
| `skill` | `agent.json` | Source file exposes a capability → a skill definition must match its interface |
| `workflow` | `agent.json` | Source file defines a process → a workflow must implement the described steps |
| `describes` | `docs.json` | Documentation describes a source file → doc must reflect current implementation |
| `manifest` | `infra.json` | Package manifest (requirements.txt) ↔ consumer (Dockerfile, CI) |
| `build` | `infra.json` | Build script references a target → path/tag changes break the build |
| `config` | `infra.json` | Configuration file consumed by another process → changes must propagate |
| `entrypoint` | `infra.json` | Entry script or test file that CI/build invokes → must exist and resolve |
| `synthesized-from` | `wiki.json` | Wiki page was synthesized from a source document → content must stay current |

### Dependency Direction Convention

The `source_file` is the **authority**. The `dependencies[].path` entries are the **downstream consumers**. Read it as:

> "If `source_file` changes, then `dependencies[].path` files need review."

For `synthesized-from` in `wiki.json`, the direction is inverted — the wiki page is the `source_file` and the upstream document is the dependency:

> "This wiki page was synthesized from `dependencies[].path` — if that source changes, the wiki page may be stale."

---

## Workflow: Adding a New Entry

### Step 1 — Identify the Contract

Ask: **"If this file changes, what other files could silently break?"**

Examples from this repo:
- `GEMINI.md` changes → agent rules in `.agents/rules/` may contradict the new constraints
- `.agents/agents.md` changes → workflow files and skill definitions may be out of sync
- `agent_app/prompts.py` changes → rules governing prompt behavior may drift
- `docs/director_context/autonomous-swarm-architecture.md` changes → `agent_app/agents.py` and `.agents/agents.md` may be stale
- `wiki/entities/tdaid-methodology.md` changes → check if source retrospectives have been updated

### Step 2 — Choose the Registry

Match the source file's domain to `agent.json`, `docs.json`, `infra.json`, or `wiki.json`.

### Step 3 — Write the Entry

```json
{
  "source_file": ".agents/rules/amnesia-sweep-defense.md",
  "verified_commit": null,
  "dependencies": [
    {
      "type": "workflow",
      "path": ".agents/workflows/executor-wrapup.md",
      "reason": "The amnesia sweep defense mandates git-add before git-clean — the executor wrapup workflow must include this step."
    }
  ]
}
```

**Key**: Set `verified_commit` to `null` for new entries. The enforcer will flag it as unstamped until you run `--stamp`.

### Step 4 — Write the `reason`

The `reason` field must answer two questions:
1. **What** is the contract? (e.g., "defines constraint X")
2. **What breaks** if it drifts? (e.g., "the rule must enforce the same constraint")

Bad: `"These files are related."` ← too vague, useless for debugging.
Good: `"GEMINI.md §1 (Amnesia Sweep Defense) is the canonical source — the rule file must mirror the same constraints verbatim."` ← specific, actionable.

---

## Running the Enforcer

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

### Reading the Output

The enforcer classifies each entry into one of four states:

| Symbol | State | Action Required |
|--------|-------|-----------------|
| ✅ | Clean | Source file's `verified_commit` matches current HEAD — no drift |
| ⚠️ | Drifted | Source file changed since last verification — review all dependencies |
| ❓ | Unstamped | Entry has `verified_commit: null` — run `--stamp` to initialize |
| ❌ | Missing | Source file no longer exists on disk — remove or update the entry |

### Resolving Drift

When the enforcer flags drift:

1. **Read the drifted entry** — note the source file and its dependencies
2. **Diff the source file** — `git diff <verified_commit>..HEAD -- <source_file>`
3. **For each dependency**: check whether the change affects the contract described in `reason`
4. **If the dependency needs updating** — update the dependent file
5. **If no update needed** — the change was benign (e.g., comment-only edit)
6. **Stamp** — run `python3 scripts/drift_enforcer.py --stamp` at session wrapup

---

## Stamping Rules

> **CRITICAL**: Only stamp during the session wrapup workflow — never mid-session.

Drift detected during development is **expected**. It means the enforcer is working. Premature stamping hides real drift by silently blessing uncommitted or unreviewed changes.

The stamping ceremony is a formal step in `.agents/workflows/session-wrapup.md`:
1. Run `python3 scripts/drift_enforcer.py` to check
2. Review every flagged entry
3. Update dependent files if needed
4. Run `python3 scripts/drift_enforcer.py --stamp`
5. Commit the updated registry JSON alongside the code changes

---

## Examples From This Repo

### agent.json: GEMINI.md → Agent Rules

```json
{
  "source_file": "GEMINI.md",
  "verified_commit": "b686b43...",
  "dependencies": [
    {
      "type": "rule",
      "path": ".agents/rules/amnesia-sweep-defense.md",
      "reason": "GEMINI.md §1 (Amnesia Sweep Defense) is the canonical source — the rule file must mirror the same constraints verbatim."
    },
    {
      "type": "workflow",
      "path": ".agents/workflows/session-start.md",
      "reason": "GEMINI.md Session Lifecycle section defines the session-start protocol — the workflow must implement the described initialization steps."
    }
  ]
}
```

### docs.json: Decision Doc → TDAID Rule + MCP Server

```json
{
  "source_file": "docs/decisions/2026-04-23_tdaid_refactor_directive.md",
  "verified_commit": "b686b43...",
  "dependencies": [
    {
      "type": "describes",
      "path": ".agents/rules/tdaid-testing-guardrails.md",
      "reason": "TDAID decision doc describes the testing philosophy — the guardrails rule must enforce the same spec-driven approach."
    },
    {
      "type": "describes",
      "path": "mcp_servers/ast_validation_mcp.py",
      "reason": "TDAID decision doc describes AST validation scope — the MCP server must implement the described validation capabilities."
    }
  ]
}
```

### infra.json: Dockerfile → Requirements + CI

```json
{
  "source_file": "docker/executor-sandbox/Dockerfile",
  "verified_commit": "5d99aba...",
  "dependencies": [
    {
      "type": "manifest",
      "path": "requirements.txt",
      "reason": "Dockerfile COPYs and pip-installs requirements.txt — any new dependency must be reflected in both files."
    },
    {
      "type": "config",
      "path": ".github/workflows/ci.yml",
      "reason": "CI installs from the same requirements.txt — Python version drift between CI and Docker causes false green tests."
    }
  ]
}
```

### wiki.json: Wiki Entity → Source Retrospective

```json
{
  "source_file": "wiki/entities/tdaid-methodology.md",
  "verified_commit": null,
  "dependencies": [
    {
      "type": "synthesized-from",
      "path": "docs/retrospectives/2026-04-23_kernel_graft_and_tdaid_stabilization.md",
      "reason": "Wiki page synthesized from this retrospective — if the source adds new TDAID constraints, the wiki page may be stale."
    },
    {
      "type": "synthesized-from",
      "path": "docs/decisions/2026-04-23_tdaid_refactor_directive.md",
      "reason": "Wiki page incorporates TDAID refactoring decisions — changes to the decision doc must be reflected in the entity page."
    }
  ]
}
```

---

## Common Mistakes

### ❌ Stamping mid-session
Stamping is a wrapup ceremony. If you stamp while still editing files, you bless incomplete work and hide real drift from the next session.

### ❌ Vague `reason` fields
`"These are related"` is useless. The reason must state **what contract exists** and **what breaks if it drifts**.

### ❌ Wrong registry domain
An agent rule ↔ workflow dependency belongs in `agent.json`, not `docs.json`. A wiki page ↔ source doc dependency belongs in `wiki.json`, not `docs.json`.

### ❌ Circular dependencies without clear authority
If A depends on B and B depends on A, designate one as the canonical authority. The non-authority file should be the `source_file` with the authority file in `dependencies`.

### ❌ Tracking vendored or generated files
Don't track files that are generated by scripts (e.g., coverage reports, lock files). Track the generator script instead.

### ❌ Forgetting to add new files to the registry
Every new rule, skill, workflow, or governance file should be added to the appropriate registry. Ask: "If this changes, does anything else need to know?"

### ❌ Using `--stamp` as a fix for drift
Stamping doesn't fix drift — it marks drift as reviewed. If the enforcer flags that `GEMINI.md` drifted from its rules, you must **review and potentially update the rules first**, then stamp.
