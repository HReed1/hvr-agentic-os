---
description: "Runs the drift enforcer to detect architectural drift across all registries, interpret the results, and guide resolution — without stamping."
---

# Drift Check

> **Trigger:** Run when you want to check the current drift state across the
> repository — during active development, before a PR, or as a diagnostic step.
> This workflow **does not stamp**. Stamping is exclusive to `/session-wrapup`.

## Step 1: Run the Drift Enforcer

Execute the enforcer against all domain registries:

```bash
python3 scripts/drift_enforcer.py
```

This scans every entry in `docs/drift_registries/` (`agent.json`, `docs.json`,
`infra.json`, `wiki.json`) and compares each file's `verified_commit` against
its latest git commit hash.

To check a single domain in isolation:

```bash
python3 scripts/drift_enforcer.py --domain agent
```

To get an overview of what percentage of repo files are tracked:

```bash
python3 scripts/drift_enforcer.py --coverage
```

## Step 2: Interpret the Output

The enforcer produces a per-domain report with four categories:

| Status | Symbol | Meaning |
|--------|--------|---------|
| **Clean** | ✅ | File's current commit matches its `verified_commit` — no changes since last stamp |
| **Drifted** | ⚠️ | File has been modified since its last stamp — dependencies need review |
| **Unstamped** | ❓ | Entry exists in the registry but has no `verified_commit` — needs initial stamp |
| **Missing** | ❌ | File tracked in the registry no longer exists on disk — entry is stale |

**Exit codes:**
- `0` — All domains clean, zero drift
- `1` — Drift detected in one or more domains

### What "Clean" means

All tracked files match their last-stamped commit. No dependency review needed.

### What "Drifted" means

A tracked source file has been modified since it was last stamped. The enforcer
lists the file, its old and new commit SHAs, and all registered dependencies.

**This is expected during active development.** Drift mid-session is normal —
it means you're changing tracked files. The important question is: *do the
dependencies listed still hold, or did your change break an assumption?*

### What "Unstamped" means

An entry was added to a registry but never stamped. This happens when you
manually add a registry entry without running `--stamp` afterward.

### What "Missing" means

A file tracked in a registry has been deleted from the repo. Either:
- The file was intentionally removed → delete the registry entry
- The file was accidentally removed → restore it

## Step 3: Fix Drifted Entries

When you see a drifted entry, the enforcer shows its dependencies:

```
  📄 GEMINI.md
     verified: b686b43a46  →  current: 1a2b3c4d5e
       📎 [RULE] .agents/rules/amnesia-sweep-defense.md
         └─ GEMINI.md §1 defines the constraint — rule file must mirror it
       📎 [WORKFLOW] .agents/workflows/session-wrapup.md
         └─ GEMINI.md Session Lifecycle defines the wrapup protocol
```

**Resolution checklist:**

1. **Read each dependency's `reason` field** — it tells you *what breaks* if the source and dependency diverge.
2. **Open both the source file and each dependency** and verify they are still consistent.
3. **If a dependency is now stale**, update it to match the source file's new state.
4. **If a dependency needs no changes**, the drift is benign and can be stamped at session-wrapup.
5. **If unexpected drift is found**, stop and consult the user before proceeding.

For **Missing** entries, either:
- Remove the entry from the registry JSON if the file was intentionally deleted
- Restore the file if the deletion was unintended

## Step 4: Stamping Discipline

> [!CAUTION]
> **This workflow does NOT stamp.** Stamping is exclusively performed during
> the `/session-wrapup` workflow (Step 2). This separation is intentional:
>
> - **Mid-session drift is expected.** You're actively changing files — of
>   course they'll drift from their last stamp. That's the enforcer working.
> - **Premature stamping masks genuine drift.** If you stamp after every
>   change, the enforcer can never catch a file that drifted without its
>   dependencies being updated.
> - **Session-wrapup is the single checkpoint.** It ensures all drift is
>   reviewed holistically before the session closes.

When you are ready to stamp (at session wrapup only):

```bash
python3 scripts/drift_enforcer.py --stamp
```

## Step 5: Commit Updated Registries

If you modified registry entries (added entries, removed stale ones, updated
dependency reasons), commit the changes:

```bash
git add docs/drift_registries/
git commit -m "chore(drift): update registry entries"
```

> [!NOTE]
> This commits **registry metadata changes** (new entries, removed entries,
> updated reasons) — not stamps. Stamp commits happen during `/session-wrapup`.

## Quick Reference

```bash
# Check all domains
python3 scripts/drift_enforcer.py

# Check one domain
python3 scripts/drift_enforcer.py --domain infra

# Coverage report
python3 scripts/drift_enforcer.py --coverage

# Stamp (session-wrapup ONLY)
python3 scripts/drift_enforcer.py --stamp
```
