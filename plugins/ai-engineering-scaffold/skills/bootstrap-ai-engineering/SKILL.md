---
name: bootstrap-ai-engineering
description: Bootstraps the AI Engineering scaffold (LLM Wiki, Drift Registry, Session Workflows, Elephant-Goldfish Verification) into a project for any agent harness (Antigravity, Claude Code, Codex, GitHub Copilot). Use when the user asks to bootstrap, scaffold, or set up the AI engineering workflow, wiki, drift registry, or session rituals in a repository.
---

# Bootstrap the AI Engineering Scaffold

This skill packages the canonical scaffold from [hvr-agentic-os](https://github.com/HReed1/hvr-agentic-os): `bin/bootstrap_ai_engineering.sh` and the four reference guides it hands to the agent. Everything under `assets/` is a synced copy of those canonical files — do not edit them here.

The scaffold is deliberately thin. The script creates the directory skeleton, copies the reference guides and helper scripts into the project, and prints an **LLM Ingest Prompt**. **You, the agent, then build the governance files** (instruction files, rules, skills, personas) by reading the guides — tailored to this project.

## Step 1: Confirm Settings With the User

Ask (or confirm sensible defaults) before running anything:

| Setting | Flag | Default |
| :--- | :--- | :--- |
| Target project directory | `--target-dir` | current working directory |
| Agent harness(es) | `--harness antigravity\|claude\|codex\|copilot\|all` (comma-separated or repeated) | the harness you are running in |
| Wiki metadata index | `--wiki-db postgres\|none` | `none` (markdown-only) |
| Postgres user / db / host / port | `--db-user`, `--db-name`, `--db-host`, `--db-port` | `$USER`, `wiki`, `localhost`, `5432` |
| Author name | `--author` | `git config user.name` |

If the target is an existing repository, suggest the user commit or stash first so the changes are easy to review. The script detects new vs. existing projects automatically.

Only offer the Postgres flags if the user chooses `--wiki-db postgres`. Never assume a database user, a cloud project (e.g. Firestore), or a task tracker the user did not ask for.

## Step 2: Run the Bootstrap Script

The script is in this skill's directory at `assets/bin/bootstrap_ai_engineering.sh`. Run it with bash (macOS, Linux, WSL, or Git Bash on Windows):

```bash
bash "<this-skill-dir>/assets/bin/bootstrap_ai_engineering.sh" \
  --target-dir "<project>" \
  --harness <harness> \
  --wiki-db <postgres|none> \
  --author "<name>"
```

It is idempotent: existing files are never overwritten (except `.agents/scaffold-config.json`, which records the chosen settings).

## Step 3: Execute the Ingest Prompt Yourself

The script ends by printing an ingest prompt between `COPY EVERYTHING BELOW THIS LINE` and `END OF PROMPT`. Because you are already the user's agent, do not ask them to copy it — show them a one-line summary, get a go-ahead, then carry out the prompt's instructions in the target project:

1. Implement the four guides in order from `<project>/docs/reference/`.
2. Apply the prompt's **harness mapping** exactly (instruction files, skill directories, Goldfish spawning method).
3. Use only the settings the prompt lists (author, wiki DB, harnesses).
4. Follow the prompt's repository block. **New repository:** use the project description the user gave (ask if they didn't) for `wiki/overview.md`, and run `git init` plus an initial commit if the prompt says git is missing. **Existing repository:** integrate only — append to `AGENTS.md`, add just the pointer/import lines to existing instruction files, seed the wiki from existing docs, and end with the list of pre-existing files you modified so the user can review `git diff`.

## Step 4: Verify and Hand Off

- Run `python3 scripts/drift_enforcer.py` in the project and confirm it executes.
- Summarize what was created, then suggest starting the first session with the session-start skill.
