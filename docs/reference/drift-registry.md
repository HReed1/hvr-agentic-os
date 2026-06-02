# Drift Registry

A pattern for tracking cross-file dependencies in codebases maintained by LLM agents.

This is an implementation guide. Copy this file into your project and tell your LLM agent to bootstrap the drift registry. The agent will create the directory structure, the enforcer script, and the schema protocol — then you start registering dependencies as you work.

## The problem

LLM agents are good at making changes across many files in one pass. They're bad at remembering that when they change `api/routes/users.py`, the OpenAPI spec needs updating, the TypeScript types need regenerating, and the Firestore security rules need to match the new field names.

Humans have the same problem. The difference is that humans build institutional memory over time — "oh right, whenever I change the auth flow I need to update the security docs." LLM agents don't accumulate this knowledge between sessions. Every session starts from scratch.

**The drift registry is that institutional memory, encoded as machine-readable JSON.**

It maps source files to their dependencies: "if this file changes, these other files need to be checked." An enforcer script compares git commit hashes to detect when a source file has changed since its dependencies were last verified. When drift is detected, it tells you exactly what to review and why.

## The core idea

Every codebase has implicit contracts between files:
- The API route handler defines field names → the frontend types must match
- The Dockerfile references a requirements file → they must stay in sync
- The security rules enforce a schema → the schema blueprint must be current
- The documentation describes a system → the system code must match the docs

These contracts are invisible. They live in developers' heads. When they break, you get subtle bugs, security holes, and documentation rot — often discovered weeks later.

The drift registry makes these contracts **explicit and enforceable**. Each contract is a JSON entry:

```json
{
  "source_file": "api/routes/users.py",
  "verified_commit": "abc123def4",
  "dependencies": [
    {
      "type": "contract",
      "path": "api/openapi.json",
      "reason": "Route handler defines response shape — OpenAPI spec must match."
    },
    {
      "type": "generated",
      "path": "src/lib/apiSchema.ts",
      "reason": "Frontend types generated from OpenAPI — cascade update required."
    }
  ]
}
```

When `api/routes/users.py` is modified (its git hash changes from `verified_commit`), the enforcer flags `api/openapi.json` and `src/lib/apiSchema.ts` for review. You fix them, then stamp the new hash. The system resets to clean.

## Architecture

```
your-project/
├── docs/
│   └── drift_registries/    # JSON registry files (one per domain)
│       ├── README.md
│       ├── api.json          # API boundary contracts
│       ├── db.json           # Database schema/security contracts
│       ├── infra.json        # Infrastructure dependency contracts
│       ├── docs.json         # Documentation accuracy contracts
│       └── agent.json        # Agent governance contracts (optional)
├── scripts/
│   └── drift_enforcer.py    # The enforcer script
└── GEMINI.md / CLAUDE.md    # Agent schema referencing the drift protocol
```

### Domain registries

Split your contracts into domains based on the boundary they track. Start with the ones that matter most for your project and add more as needed:

| Registry | Domain | What it tracks |
|----------|--------|----------------|
| `api.json` | API boundaries | Route handlers ↔ specs ↔ frontend types ↔ tests |
| `db.json` | Database contracts | Schema definitions ↔ security rules ↔ migration files |
| `infra.json` | Infrastructure | Dockerfiles ↔ requirements ↔ CI configs ↔ build scripts |
| `docs.json` | Documentation | Docs ↔ the source code they describe |
| `agent.json` | Agent governance | Source files ↔ agent rules/skills/workflows that govern them |

> **Start small.** You don't need all five registries on day one. Start with the domain where drift causes the most pain — usually `api.json` or `infra.json` — and expand as you build trust in the system.

### Registry schema

Each registry file is a JSON object with an `entries` array:

```json
{
  "_meta": {
    "last_updated": "2026-05-31T22:00:00Z"
  },
  "entries": [
    {
      "source_file": "path/to/file.py",
      "verified_commit": "abc123def456...",
      "dependencies": [
        {
          "type": "contract",
          "path": "path/to/dependent_file.ts",
          "reason": "Why these files must stay in sync."
        }
      ]
    }
  ]
}
```

#### Field definitions

| Field | Required | Description |
|-------|----------|-------------|
| `source_file` | Yes | Relative path from repo root to the tracked file |
| `verified_commit` | Yes | Full git commit SHA when this mapping was last verified. Set to `null` for new entries |
| `dependencies[].type` | Yes | The relationship type (see reference below) |
| `dependencies[].path` | Yes | Relative path to the dependent file |
| `dependencies[].reason` | **Yes** | Human-readable explanation of what to check when drift is detected. This is the most important field — it's the debugging blueprint for future sessions |

#### Dependency types

**For engineering registries** (`api.json`, `db.json`, `infra.json`, `docs.json`):

| Type | Meaning | Example |
|------|---------|---------|
| `contract` | Bidirectional parity requirement | API route response shape must match OpenAPI spec |
| `generated` | Output auto-generated from source | TypeScript types generated from OpenAPI spec |
| `data-layer` | Backend writes ↔ frontend reads | Webhook writes fields that frontend must handle |
| `runtime` | Runtime code dependency | Route handler imports a shared module |
| `schema` | Schema that validation enforces | Blueprint defines shapes, rules validate them |
| `enforcement` | Rules file enforcing a schema | Security rules enforce a schema blueprint |
| `config` | Configuration dependency | CI uses a linter config for a build step |
| `consumer` | File that imports/uses the source | One module imports another |
| `entrypoint` | Module referenced as entry point | Dockerfile CMD references `api/main.py` |
| `build` | Build pipeline reference | CI config references a Dockerfile |
| `manifest` | Dependency manifest | Dockerfile installs from requirements.txt |
| `spec` | Specification defining expected behavior | Config headers implement a security spec |
| `describes` | Documentation describing source behavior | README describes how the API works |
| `source-of-truth` | Canonical source for a derived file | OpenAPI spec is the source for generated types |
| `synthesized-from` | Wiki page built from a source doc | Wiki entity page synthesized from architecture doc |

**For agent governance** (`agent.json` only):

| Type | Path pattern | Meaning |
|------|-------------|---------|
| `rule` | `.agents/rules/*.md` or `.claude/rules/*.md` | Source file must comply with behavioral constraints |
| `skill` | `.agents/skills/*/SKILL.md` | Source file is a target for the skill's logic |
| `workflow` | `.agents/workflows/*.md` | Source file is read/modified by the workflow |

> **Critical rule:** `agent.json` is the **only** registry that tracks agent artifacts as dependencies. All other registries track source-file-to-source-file engineering contracts. Never add agent rules as dependencies in `api.json`, `db.json`, etc.

## The enforcer script

The enforcer is a standalone Python script (~200 lines) with zero external dependencies. It reads registry JSON files, compares `verified_commit` against each file's current `git log` hash, and reports drift.

### Usage

```bash
# Check all domains for drift (exit code 1 if drift detected)
python3 scripts/drift_enforcer.py

# Check a specific domain
python3 scripts/drift_enforcer.py --domain api

# After reviewing flagged items, stamp current hashes
python3 scripts/drift_enforcer.py --stamp

# Report coverage: what percentage of repo files are tracked
python3 scripts/drift_enforcer.py --coverage
```

### Enforcer script

Copy this into `scripts/drift_enforcer.py`:

```python
#!/usr/bin/env python3
"""
Universal Drift Enforcer

Reads registry JSON files from docs/drift_registries/ and compares each
entry's `verified_commit` against the file's latest git commit hash.

Usage:
  python3 scripts/drift_enforcer.py                 # Check all domains
  python3 scripts/drift_enforcer.py --domain api    # Check one domain
  python3 scripts/drift_enforcer.py --stamp         # Stamp current hashes
  python3 scripts/drift_enforcer.py --coverage      # Report coverage
"""

import json
import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

REGISTRIES_DIR = Path(__file__).resolve().parent.parent / "docs" / "drift_registries"
REPO_ROOT = Path(__file__).resolve().parent.parent


def git_latest_commit(filepath: str) -> str | None:
    """Return the full SHA of the last commit that touched `filepath`."""
    abs_path = REPO_ROOT / filepath
    if not abs_path.exists():
        return None
    try:
        result = subprocess.run(
            ["git", "log", "--format=%H", "-1", "--", filepath],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        sha = result.stdout.strip()
        return sha if sha else None
    except Exception:
        return None


def load_registry(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def save_registry(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def stamp_hashes(reg_path: Path, registry: dict) -> None:
    """Write the current git hash of each source file into the registry."""
    count = 0
    for entry in registry.get("entries", []):
        sha = git_latest_commit(entry["source_file"])
        if sha:
            entry["verified_commit"] = sha
            count += 1
    if "_meta" not in registry:
        registry["_meta"] = {}
    registry["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_registry(reg_path, registry)
    print(f"✅ [{reg_path.stem.upper()}] Stamped {count} entries.")


def check_drift(domain: str, registry: dict) -> bool:
    """Compare verified_commit against current HEAD. Returns True if drift found."""
    entries = registry.get("entries", [])
    if not entries:
        return False

    drifted, clean, missing, unstamped = [], [], [], []

    for entry in entries:
        source = entry["source_file"]
        verified = entry.get("verified_commit")
        current = git_latest_commit(source)

        if current is None:
            missing.append(entry)
        elif verified is None:
            unstamped.append({**entry, "current_commit": current})
        elif verified != current:
            drifted.append({**entry, "current_commit": current})
        else:
            clean.append(entry)

    # Print report
    total = len(entries)
    print(f"\n{'=' * 72}")
    print(f"  DRIFT REPORT: {domain.upper()}")
    print(f"{'=' * 72}")
    print(f"  Tracked: {total}  ✅ Clean: {len(clean)}  "
          f"⚠️  Drifted: {len(drifted)}  ❓ Unstamped: {len(unstamped)}  "
          f"❌ Missing: {len(missing)}")

    if drifted:
        print(f"\n{'-' * 72}")
        print("  ⚠️  DRIFTED FILES — Dependencies need review")
        print(f"{'-' * 72}")
        for entry in drifted:
            print(f"\n  📄 {entry['source_file']}")
            print(f"     verified: {entry['verified_commit'][:10]}  →  "
                  f"current: {entry['current_commit'][:10]}")
            for dep in entry.get("dependencies", []):
                print(f"       📎 [{dep['type'].upper()}] {dep['path']}")
                print(f"         └─ {dep['reason']}")

    if unstamped:
        print(f"\n{'-' * 72}")
        print("  ❓ UNSTAMPED — Run with --stamp to initialize")
        print(f"{'-' * 72}")
        for entry in unstamped:
            print(f"  📄 {entry['source_file']}  "
                  f"(current: {entry['current_commit'][:10]})")

    if missing:
        print(f"\n{'-' * 72}")
        print("  ❌ MISSING — Files no longer exist")
        print(f"{'-' * 72}")
        for entry in missing:
            print(f"  📄 {entry['source_file']}")

    if not drifted and not unstamped and not missing:
        print(f"\n  ✅ All {total} files in '{domain}' are clean.")

    print(f"{'=' * 72}")
    return bool(drifted or unstamped or missing)


def report_coverage() -> None:
    """Report what percentage of repo files are tracked."""
    tracked = set()
    for reg_path in REGISTRIES_DIR.glob("*.json"):
        try:
            for entry in load_registry(reg_path).get("entries", []):
                tracked.add(entry["source_file"])
        except Exception:
            pass

    result = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True,
        cwd=REPO_ROOT, check=True,
    )
    skip_ext = {".png", ".svg", ".ico", ".jpg", ".jpeg", ".gif", ".webp"}
    skip_names = {"package-lock.json", "uv.lock"}
    eligible = {
        f for f in result.stdout.splitlines()
        if Path(f).suffix.lower() not in skip_ext
        and Path(f).name not in skip_names
        and not f.startswith("public/")
    }
    covered = eligible & tracked
    pct = (len(covered) / len(eligible) * 100) if eligible else 0

    print(f"{'=' * 72}")
    print(f"  DRIFT COVERAGE: {len(covered)}/{len(eligible)} files ({pct:.1f}%)")
    print(f"{'=' * 72}")
    if eligible - tracked:
        print("  Top untracked:")
        for f in sorted(eligible - tracked)[:10]:
            print(f"    📄 {f}")
    print(f"{'=' * 72}")


def main():
    parser = argparse.ArgumentParser(description="Universal Drift Enforcer")
    parser.add_argument("--domain", help="Check a specific domain")
    parser.add_argument("--stamp", action="store_true", help="Stamp current hashes")
    parser.add_argument("--coverage", action="store_true", help="Report coverage")
    args = parser.parse_args()

    if not REGISTRIES_DIR.exists():
        print(f"❌ Registry directory not found: {REGISTRIES_DIR}")
        sys.exit(1)

    if args.coverage:
        report_coverage()
        sys.exit(0)

    if args.domain:
        files = [REGISTRIES_DIR / f"{args.domain}.json"]
        if not files[0].exists():
            print(f"❌ Domain not found: {files[0]}")
            sys.exit(1)
    else:
        files = sorted(REGISTRIES_DIR.glob("*.json"))

    overall_drift = False
    for reg_path in files:
        registry = load_registry(reg_path)
        if args.stamp:
            stamp_hashes(reg_path, registry)
        else:
            if check_drift(reg_path.stem, registry):
                overall_drift = True

    if not args.stamp:
        if overall_drift:
            print("\n  🚨 Drift detected. Review and run --stamp when ready.\n")
            sys.exit(1)
        else:
            print("\n  🌟 All domains clean. Zero drift.\n")


if __name__ == "__main__":
    main()
```

## Agent schema protocol

Add this section to your agent configuration file (`GEMINI.md` for Antigravity, `CLAUDE.md` for Claude Code, `AGENTS.md` for Codex):

```markdown
## Drift Registry Protocol

This project uses a drift registry system to track cross-file dependencies.
Registries live at `docs/drift_registries/*.json`. The enforcer script is at
`scripts/drift_enforcer.py`.

### When to add a registry entry

Add an entry when ANY of these occur:
1. A new source file is created that depends on or is depended upon by existing files
2. A new dependency relationship is discovered during development
3. An existing file gains a new consumer

### How to add an entry

1. Determine the correct domain registry (api, db, infra, docs, agent)
2. Ask: "If this file changes, what other files could break?"
3. Add a new object to the `entries` array with `verified_commit: null`
4. Run `python3 scripts/drift_enforcer.py --stamp` to initialize

### When to run the enforcer

- **End of every session** — before committing, run the enforcer to check for drift
- **Before merging PRs** — ensure no contracts have silently broken
- **Periodically** — as a hygiene check

### Stamping rules

> IMPORTANT: Only stamp at session end, never mid-session. Drift detected
> during development is expected — it means the enforcer is working. Save
> stamping for the wrapup step to preserve the system as a safety net.

### If drift is detected

1. Review the flagged files and their dependency reasons
2. If the changes are intentional: update the dependent files, then stamp
3. If the changes are unexpected: stop and consult the user
4. Always explain what was reviewed in the session retrospective
```

## Session integration

### Session wrapup workflow

If your project uses session start/wrapup workflows, the drift enforcer integrates as a wrapup step:

```markdown
## Step N: Enforce Drift Checks

1. Run the drift enforcer:
   ```bash
   python3 scripts/drift_enforcer.py
   ```
2. If drift is detected:
   - Review flagged files to ensure changes were intentional
   - If unexpected drift is found, stop and consult the user
   - Otherwise, stamp the new baseline:
     ```bash
     python3 scripts/drift_enforcer.py --stamp
     ```
3. Commit the updated registries:
   ```bash
   git add docs/drift_registries/
   git commit -m "chore: stamp drift registries"
   ```
```

> **Critical:** This is the single correct stamping point per session. Do NOT stamp mid-session during active development.

## CI integration (optional)

Add the enforcer as a CI check to prevent merging PRs with unreviewed drift:

```yaml
# .github/workflows/drift-check.yml
name: Drift Check
on: [pull_request]
jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history needed for git log
      - run: python3 scripts/drift_enforcer.py
```

This fails the PR if any tracked file has drifted since its last stamp — forcing the developer (or agent) to review dependencies before merging.

## Bootstrap instructions

Tell your LLM agent:

> **"Bootstrap a drift registry for this project. Follow the guide in this file: [path to this file]. Create `docs/drift_registries/` with a `README.md`, create `scripts/drift_enforcer.py`, add the Drift Registry Protocol to [GEMINI.md|CLAUDE.md|AGENTS.md], and register the 5 most critical cross-file dependencies you can find in the codebase."**

The agent should:
1. Create `docs/drift_registries/` directory with `README.md`
2. Create `scripts/drift_enforcer.py` (copy from the script section above)
3. Scan the codebase for obvious cross-file contracts (imports, configs, generated files)
4. Create initial registry files with 3-5 entries each
5. Add the protocol to the agent configuration file
6. Run `--stamp` to initialize all hashes
7. Run `--coverage` to report how much of the repo is tracked

## Common mistakes to avoid

1. **Tracking everything.** Not every file needs a registry entry. Focus on files where drift causes real damage — API contracts, security rules, generated types, infrastructure configs. Tracking `README.md` → `package.json` is overkill.

2. **Missing the `reason` field.** Every dependency MUST have a reason. It's the debugging blueprint for future agents and developers. "Related file" is not a reason. "Route handler defines the `userId` claim format — security rules must validate the same format" is.

3. **Stamping mid-session.** If you stamp after every file edit, the enforcer never catches anything. Stamp once at session end, after reviewing all drift.

4. **Putting agent rules in non-agent registries.** Only `agent.json` tracks `.agents/` or `.claude/` artifacts. Engineering registries track source-to-source contracts.

5. **Tracking generated output as source.** Track the source that generates the output, not the output itself. Exception: track generated files that are critical contract boundaries (e.g., TypeScript types that the frontend depends on).

6. **Forgetting to remove deleted files.** If a source file is deleted, remove its entry. The enforcer flags missing files with ❌, but stale entries add noise.

## Why this works

The drift registry works for the same reason the LLM Wiki works: it offloads bookkeeping from humans to a system that doesn't forget.

Every project has hidden dependencies between files. Experienced developers know some of them. New developers know none. LLM agents rediscover them from scratch each session — or worse, they don't discover them at all and silently break a contract.

The registry makes the implicit explicit. The enforcer makes the explicit enforceable. And the `reason` field on every dependency ensures that when drift is detected, the reviewer knows exactly what to check — whether that reviewer is a human, an LLM agent, or a CI pipeline.

## Attribution

This pattern emerged from the development of [hvr-informatics](https://github.com/harrisonreed/hvr-informatics), where cross-file drift between API routes, Firestore security rules, agent governance artifacts, and frontend types was a recurring source of bugs. The Universal Drift Enforcer was designed to make these contracts machine-readable and enforceable by both humans and LLM agents.
