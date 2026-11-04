# AI Engineering Scaffold — Plugin

A shareable package of the AI Engineering scaffold from [hvr-agentic-os](https://github.com/HReed1/hvr-agentic-os): the **LLM Wiki**, **Drift Registry**, **Session Workflows**, and **Elephant-Goldfish Verification**. It works with Antigravity, Claude Code, OpenAI Codex, and GitHub Copilot.

> [!IMPORTANT]
> This plugin is a distribution vehicle, not a second implementation. The canonical scaffold is [`bin/bootstrap_ai_engineering.sh`](../../bin/bootstrap_ai_engineering.sh) plus the guides in [`docs/reference/`](../../docs/reference/). `skills/bootstrap-ai-engineering/assets/` holds synced copies — edit the canonical files, then run `python3 scripts/sync_scaffold_plugin.py`.

## How It Works

1. The `bootstrap-ai-engineering` skill runs the bundled `bootstrap_ai_engineering.sh`. The script creates the skeleton (`wiki/`, `docs/drift_registries/`, `.agents/`), copies in the reference guides and `scripts/drift_enforcer.py`, and prints an **LLM Ingest Prompt** tailored to your harness.
2. Your agent implements the four guides from that prompt, writing the instruction files, rules, skills, and Goldfish personas for *your* project.

| `--harness` | Instruction files the agent writes | Skills directory |
| :--- | :--- | :--- |
| `antigravity` | `AGENTS.md` + `GEMINI.md` | `.agents/skills/` |
| `claude` | `AGENTS.md` + `CLAUDE.md` (starts with `@AGENTS.md`) | `.claude/skills/` |
| `codex` | `AGENTS.md` only (kept under 32 KiB) | `.agents/skills/` |
| `copilot` | `AGENTS.md` + `.github/copilot-instructions.md` | `.agents/skills/` |

Other options: `--wiki-db postgres|none` (default `none`), `--db-user`, `--db-name`, `--db-host`, `--db-port`, `--author`, `--target-dir`. Run with `--help` for details.

## Install

**Easiest: ask the agent you already use.** Paste one of these into it, approve the commands, then restart the session:

| Harness | Request |
| :--- | :--- |
| Antigravity | *"Clone https://github.com/HReed1/hvr-agentic-os to ~/Projects/hvr-agentic-os and run `plugins/ai-engineering-scaffold/install.sh --harness antigravity`."* |
| Claude Code | `/plugin marketplace add HReed1/hvr-agentic-os` then `/plugin install ai-engineering-scaffold@hvr-agentic-os` — or ask Claude to run `install.sh --harness claude` from a clone. |
| Codex | *"Clone https://github.com/HReed1/hvr-agentic-os to ~/Projects/hvr-agentic-os and run `plugins/ai-engineering-scaffold/install.sh --harness codex`."* |
| GitHub Copilot | *"Clone https://github.com/HReed1/hvr-agentic-os to ~/Projects/hvr-agentic-os and run `plugins/ai-engineering-scaffold/install.sh --harness copilot`."* |

What `install.sh` links (symlinks, so `git pull` updates every install):

| Harness | Destination |
| :--- | :--- |
| Antigravity | `~/.gemini/config/plugins/ai-engineering-scaffold` → this plugin |
| Claude Code | `~/.claude/skills/bootstrap-ai-engineering` → the skill |
| Codex | `~/.agents/skills/bootstrap-ai-engineering` → the skill |
| GitHub Copilot | `~/.copilot/extensions/ai-engineering-scaffold` → `copilot/`, and `~/.copilot/skills/bootstrap-ai-engineering` → the skill |

Uninstall with `--uninstall`. Windows users need Git Bash or WSL (the scaffold is a bash script).

## Usage

Open your agent in the target project and ask:

- **New project** (run `git init` first): *"Bootstrap the AI engineering scaffold in this repo. It's a new project: <what it will build>."*
- **Existing project** (commit or stash first): *"Bootstrap the AI engineering scaffold in this repo. It's an existing project — keep my current instructions and docs, and seed the wiki from what's already here."*

The script detects which case applies. For existing repos it never overwrites files, and the ingest prompt switches to integration mode (append to `AGENTS.md`, seed the wiki from existing docs, list every file touched). Full walkthrough: [Adopting the Scaffold in Your Own Repos](../../README.md#adopting-the-scaffold-in-your-own-repos).

Without a plugin, run the script directly and paste the printed prompt into any agent:

```bash
bash skills/bootstrap-ai-engineering/assets/bin/bootstrap_ai_engineering.sh --harness codex --target-dir /path/to/project
```
