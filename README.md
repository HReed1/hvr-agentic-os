# HVR Agentic OS

> 📰 **As seen on [HVRInformatics.com](https://hvrinformatics.com/blog)**

A Zero-Trust multi-agent operating system built on [Google's Agent Development Kit (ADK)](https://google.github.io/adk-docs/), and a portable **AI Engineering scaffold** for structuring how LLM agents maintain knowledge, track dependencies, and work across sessions.

---

## What's In This Repo

**Three things:**

1. **A Multi-Agent Swarm** — Four specialized AI agents (Director, Executor, QA Engineer, Auditor) collaborating through strict tool segregation, adversarial verification, and DLP-enforced sandbox boundaries. → [See `agent_app/README.md`](agent_app/README.md)

2. **A Portable AI Engineering Scaffold** — Battle-tested patterns for LLM-maintained knowledge bases, cross-file dependency tracking, and structured session workflows. Harness-agnostic (Antigravity, Claude Code, Codex, GitHub Copilot) and adoptable into any codebase. → Keep reading.

3. **AI Engineering Scaffold Plugin (`plugins/ai-engineering-scaffold/`)** — The same scaffold packaged for one-command install into Antigravity, Claude Code, Codex, or GitHub Copilot (CLI extension). → [See `plugins/ai-engineering-scaffold/README.md`](plugins/ai-engineering-scaffold/README.md)


---

## AI Engineering Scaffold

The patterns below solve four problems that every LLM-assisted codebase eventually hits:

| Problem | Solution | Reference Guide |
|---------|----------|----------------|
| Knowledge evaporates between sessions | **LLM Wiki** — persistent, agent-maintained knowledge base | [llm-wiki-antigravity.md](docs/reference/llm-wiki-antigravity.md) |
| File changes silently break contracts | **Drift Registry** — machine-readable dependency tracking | [drift-registry.md](docs/reference/drift-registry.md) |
| Sessions start cold and end without trace | **Session Workflows** — structured open→work→close lifecycle | [session-workflows.md](docs/reference/session-workflows.md) |
| Single-context agents self-validate unstated assumptions | **Elephant-Goldfish Verification** — stateless zero-context subagent review & epistemic hygiene *(adapted from [google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model))* | [elephant-goldfish-verification.md](docs/reference/elephant-goldfish-verification.md) |

These four systems reinforce each other. The wiki accumulates knowledge across sessions, the drift registry protects it from silent breakage, the session workflows ensure both are maintained at every session boundary, and the Elephant-Goldfish subagent gate prevents within-session echo chambers and self-glazing when drafting specs or auditing drifted contracts.

### How It Works

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  /session-start│     │  Engineering   │     │/session-wrapup │
│                │     │    Session     │     │                │
│ • Load wiki    │────▶│               │────▶│ • Commit work  │
│ • Check drift  │     │ Actual coding, │     │ • Enforce drift│
│ • Set focus    │     │ debugging, etc │     │ • Write retro  │
│                │     │               │     │ • Update wiki  │
└────────────────┘     └────────────────┘     └────────────────┘
```

---

## Quick Start (AI Engineering Scaffold)

### Prerequisites

- Python 3.11+
- Git
- PostgreSQL (optional — for the wiki metadata index)
- An LLM agent (Antigravity, Claude Code, Codex, GitHub Copilot, etc.)

### 1. Bootstrap the Scaffold

```bash
chmod +x bin/bootstrap_ai_engineering.sh
./bin/bootstrap_ai_engineering.sh --harness claude --target-dir /path/to/project
```

| Option | Values | Default |
| :--- | :--- | :--- |
| `--harness` | `antigravity`, `claude`, `codex`, `copilot`, `all` (comma-separated or repeated) | `antigravity` |
| `--wiki-db` | `postgres`, `none` | `none` (markdown-only wiki) |
| `--db-user` / `--db-name` / `--db-host` / `--db-port` | Postgres connection (with `--wiki-db postgres`) | `$USER` / `wiki` / `localhost` / `5432` |
| `--author` | Name used in retrospectives and wiki pages | `git config user.name` |
| `--target-dir` | Project to scaffold | current directory |

The harness decides which instruction files and skill directories the agent creates:

| Harness | Instruction files | Skills |
| :--- | :--- | :--- |
| `antigravity` | `AGENTS.md` + `GEMINI.md` | `.agents/skills/` |
| `claude` | `AGENTS.md` + `CLAUDE.md` (imports `@AGENTS.md`) | `.claude/skills/` |
| `codex` | `AGENTS.md` only (kept under Codex's 32 KiB limit) | `.agents/skills/` |
| `copilot` | `AGENTS.md` + `.github/copilot-instructions.md` | `.agents/skills/` |

This creates:
- `wiki/` — Directory structure for the LLM-maintained knowledge base
- `docs/drift_registries/` — Empty registry templates
- `docs/retrospectives/` — Session retrospective archive
- `.agents/` — Agent governance (skills, rules)
- `docs/reference/` — The four reference guides (copied in when scaffolding another repo)
- `scripts/` — Utility scripts (drift enforcer; wiki DB scripts with `--wiki-db postgres`)
- `.agents/scaffold-config.json` — The chosen harness, DB, and author settings

The script is idempotent — run it multiple times safely.

### 2. Feed the Reference Guides to Your LLM

The bootstrap script prints an **LLM Ingest Prompt** at the end, tailored to your harness and settings. Copy it and paste it into your LLM agent. It instructs the agent to read and implement the four reference guides in order:

1. **[LLM Wiki](docs/reference/llm-wiki-antigravity.md)** — Sets up wiki conventions, page templates, ingest/query/lint workflows, and (optionally) the Postgres metadata index
2. **[Drift Registry](docs/reference/drift-registry.md)** — Sets up dependency tracking, the enforcer script, and registry schemas
3. **[Session Workflows](docs/reference/session-workflows.md)** — Sets up `/session-start` and `/session-wrapup` workflows that tie the wiki and drift registry together
4. **[Elephant-Goldfish Verification](docs/reference/elephant-goldfish-verification.md)** — Sets up `.agents/rules/no-glazing-and-epistemic-hygiene.md`, the 3 stateless Goldfish reviewer personas (`.agents/personas/goldfish-*.md`), and the `/goldfish-review` subagent verification skill

After ingestion, your agent will have created `AGENTS.md` plus its harness-specific instruction file, skills (including slash-command workflows), and governance structure for your project.

### 3. Initialize the Wiki Database (Optional)

If you bootstrapped with `--wiki-db postgres`, the ingest prompt has the agent run this with your connection settings:

```bash
python3 scripts/wiki_db_init.py --database wiki --host localhost --port 5432 --user "$USER"
```

This creates the `wiki` database with tables for page metadata, cross-references, and activity logging. The wiki works without the database (it's just markdown files), but the database enables fast SQL queries across all pages.

### 4. Start Your First Clean Session

Once the bootstrap session finishes creating your governance files and initial wiki seed, **commit the scaffold and open a fresh, clean agent session** (so your context window isn't already filled by the four reference guides). Tell your LLM agent:

```
/session-start
```

The agent will load the wiki overview, check for outstanding work, run the drift enforcer, and ask you for your session focus. When you're done:

```
/session-wrapup
```

The agent commits your work, enforces drift checks, generates a retrospective, and optionally ingests significant findings into the wiki.

> [!TIP]
> **Onboarding an existing codebase?** Don't try to ingest the entire repo, audit bugs, and build new features all inside the bootstrap session. Follow the **[4-Session Onboarding Playbook](#the-4-session-onboarding-playbook-for-existing-repos)** below to work with (not against) LLM context window limits.

---

## Adopting the Scaffold in Your Own Repos

The scaffold is portable: it works in a brand-new repository or an existing one, with whichever agent harness you already use. There are two steps: **get the scaffold** (install the plugin, or just clone this repo), then **apply it** to your project.

### Step 1: Install the Plugin Using Your Current Harness

You don't need to install anything by hand. Paste the matching request into the agent you already use; it clones this repo and links the plugin into its own harness. Approve the commands when it asks (it writes outside your project, to your home directory).

| Your harness | What to tell your agent |
| :--- | :--- |
| **Antigravity** | *"Clone https://github.com/HReed1/hvr-agentic-os to ~/Projects/hvr-agentic-os (skip if it's already there) and run `plugins/ai-engineering-scaffold/install.sh --harness antigravity`."* |
| **Claude Code** | Type `/plugin marketplace add HReed1/hvr-agentic-os`, then `/plugin install ai-engineering-scaffold@hvr-agentic-os`. Or tell Claude: *"Clone https://github.com/HReed1/hvr-agentic-os and run `plugins/ai-engineering-scaffold/install.sh --harness claude`."* |
| **OpenAI Codex** | *"Clone https://github.com/HReed1/hvr-agentic-os to ~/Projects/hvr-agentic-os and run `plugins/ai-engineering-scaffold/install.sh --harness codex`."* (Codex's sandbox will ask to allow network access and writes to `~/.agents/skills/`.) |
| **GitHub Copilot** | *"Clone https://github.com/HReed1/hvr-agentic-os to ~/Projects/hvr-agentic-os and run `plugins/ai-engineering-scaffold/install.sh --harness copilot`."* |

Then **restart the agent session** so it discovers the new `bootstrap-ai-engineering` skill. Using several harnesses? Pass `--harness all` (or a comma-separated list). To update later, `git pull` the clone — installs are symlinks.

> [!TIP]
> **No plugin, no problem.** Every step below also works by running the script from a clone and pasting its printed prompt into any agent: `~/Projects/hvr-agentic-os/bin/bootstrap_ai_engineering.sh --harness <harness> --target-dir <project>`.

### Step 2a: Start a New Repository From Scratch

```bash
mkdir my-project && cd my-project && git init
```

Open your agent in `my-project/` and say:

> *"Bootstrap the AI engineering scaffold in this repo. It's a new project: <one or two sentences about what it will build or manage>."*

The script detects an empty project and has the agent ask for (or use) your description to write `wiki/overview.md`, then create `AGENTS.md` + your harness's instruction file, the drift registries, the session-start / session-wrapup skills, and the Goldfish review personas. If you skipped `git init`, the script warns you and the agent initializes git before verifying the drift enforcer.

### Step 2b: Initialize an Existing Repository

Commit or stash your work first so you can review exactly what changes:

```bash
cd my-existing-repo && git status   # clean working tree
```

Open your agent in the repo and say:

> *"Bootstrap the AI engineering scaffold in this repo. It's an existing project — keep my current instructions and docs, investigate the repo and ask me any clarifying questions you need, and seed an initial wiki covering the main areas of the project."*

The script never overwrites existing files, and it detects existing content (README, `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`, tracked files). The ingest prompt then switches to **integration mode**:
- The agent appends protocol sections to `AGENTS.md` instead of replacing it, and only adds the import/pointer lines your harness needs to existing instruction files.
- Alongside investigating your `README.md`, `docs/`, and code layout, the agent asks clarifying questions about the repository's architecture, domain, or priorities, and uses both to write `wiki/overview.md` and an initial set of high-level wiki pages covering the main areas of the repo.
- It registers initial cross-file dependencies in `docs/drift_registries/` and finishes with a list of every pre-existing file it touched. Review with `git diff` and commit.

---

### The 4-Session Onboarding Playbook for Existing Repos

Because LLM context windows are finite, **do not try to bootstrap the scaffold, deeply ingest an entire existing codebase, audit technical debt, and build new features all inside a single session.** During bootstrap, reading the four reference guides and generating your governance files (`AGENTS.md`, skills, rules, Goldfish personas) already consumes a substantial portion of the session's context budget.

To get deep, high-signal wiki pages and accurate drift registries without context degradation, split onboarding across **four focused, clean sessions**:

```
┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│  Session 1: Bootstrap│   │ Session 2: Deep Wiki │   │  Session 3: Audit &  │   │ Session 4+: Feature  │
│  & High-Level Seed   │──▶│  & Drift Ingestion   │──▶│  Prioritization      │──▶│  Development         │
│                      │   │   (Clean Session)    │   │   (Clean Session)    │   │   (Clean Sessions)   │
│ • Install scaffold   │   │ • Deep-dive docs/code│   │ • Critical issues    │   │ • Build new features │
│ • Answer repo Q&A    │   │ • Build entities &   │   │ • Low-hanging fruit  │   │ • Execute roadmap    │
│ • Initial overview   │   │   concepts pages     │   │ • Long-term robust   │   │ • Compounding wiki & │
│   & main-area wiki   │   │ • Map critical drift │   │   optimizations/fixes│   │   drift protection   │
│ • Commit & close     │   │   registries         │   │ • File synthesis doc │   │                      │
└──────────────────────┘   └──────────────────────┘   └──────────────────────┘   └──────────────────────┘
```

#### Session 1 — Bootstrap & Initial High-Level Wiki Seed

Run the bootstrap command from [Step 2b](#step-2b-initialize-an-existing-repository) above. During this session, the agent:
1. Reads the four reference guides and generates your harness instruction files, session workflows, and Goldfish verification personas.
2. Explores your repository's top-level layout and existing documentation (`README.md`, `docs/`), and asks you targeted questions about the project's purpose, architecture, and non-obvious conventions.
3. Seeds `wiki/overview.md`, `wiki/index.md`, and foundational wiki pages for the main areas of the repo, plus baseline drift registry entries.

Once `python3 scripts/drift_enforcer.py` runs cleanly, review `git diff`, commit the scaffold, and **close the session** so your next session starts with a fresh context window.

#### Session 2 — Deep Wiki & Drift Registry Ingestion *(New Clean Session)*

Open a brand-new session with a full context window. Now that the wiki protocol and session skills are installed, dedicate this session to thoroughly mapping the repository's critical entities, concepts, and cross-file contracts:

> *"`/session-start` — For this session, let's do a comprehensive, deep-dive ingestion of the repository into the wiki and drift registries. Inspect our codebase, configs, scripts, and existing docs to:*
> *1. Create or expand `wiki/entities/` pages for all critical systems, services, modules, CLI tools, and data pipelines (with source citations and `[[wikilinks]]`).*
> *2. Create or expand `wiki/concepts/` pages for our core architectural patterns, domain models, state/data flows, and operational invariants.*
> *3. Populate `docs/drift_registries/` (e.g., `code.json`, `infra.json`, `docs.json`, `wiki.json`) with the critical cross-file dependencies where changing one file silently breaks another (schemas ↔ handlers, configs ↔ entrypoints, scripts ↔ docs, source docs ↔ wiki pages).*
> *Ask me questions whenever intent or domain context isn't clear from the code, then wrap up with `/session-wrapup`."*

> [!NOTE]
> **Very large monorepo or codebase?** Split Session 2 across two or three clean sessions by subsystem or domain (e.g., Session 2a: core backend & data layer; Session 2b: frontend, CLI & infrastructure) so the agent can read actual implementation files deeply rather than skimming directory trees.

#### Session 3 — Codebase Audit: Critical Issues, Quick Wins & Long-Term Optimizations *(New Clean Session)*

Start another fresh session. With the wiki and drift registries populated, your agent now has a structured architectural map of the repo and can audit the codebase with high precision instead of guessing from cold file searches:

> *"`/session-start` — Using the wiki and a targeted inspection of the codebase, perform an engineering audit of the repository. Do not write feature code yet; instead, analyze the system and organize findings into three prioritized tiers:*
> *1. **Current Most Critical Issues:** Active bugs, fragile or undocumented contracts, security/reliability risks, or broken test/build paths that need immediate attention.*
> *2. **Low-Hanging Fruit:** High-leverage quick wins — straightforward bug fixes, dead code or config cleanup, missing drift coverage, or small developer-experience improvements we can knock out quickly.*
> *3. **Long-Term Robust Optimizations & Bug Fixes:** Deeper architectural refactors, performance bottlenecks, test-suite hardening, and systemic reliability improvements.*
> *Run `/goldfish-review` on your proposed findings to challenge any unstated assumptions, file the final prioritized roadmap as a synthesis page in `wiki/synthesis/` (and update `wiki/index.md`), and close with `/session-wrapup`."*

#### Session 4+ — Feature Development & Execution *(New Clean Sessions)*

From your fourth session onward, your repository is fully onboarded: the wiki captures the architecture, the drift registries guard critical contracts, and `wiki/synthesis/` holds a vetted backlog of critical fixes, quick wins, and long-term optimizations.

Start each new session with `/session-start`, pick either the new features you want to build or items from your audit roadmap, and finish each session with `/session-wrapup` so every change compounds back into the wiki and drift registries.

### Options Worth Knowing

Mention these in your request (or pass them to the script) when they apply:

- **Postgres wiki index:** *"use the Postgres wiki index as user `<db-user>`"* → `--wiki-db postgres --db-user <db-user>` (default is a markdown-only wiki).
- **Author name:** *"author is `<name>`"* → `--author "<name>"` (default: `git config user.name`).
- **Task tracking (e.g. Cadence, Jira, Linear):** not included by default — the scaffold never assumes an external tracker. Ask your agent to wire one into the session-start/session-wrapup skills afterward (see [session-workflows.md](docs/reference/session-workflows.md)).

Once bootstrapped, use the session-start and session-wrapup skills to structure every session. The agent handles everything else: maintaining the wiki, keeping registries current, and enforcing the governance rules as you work.

---

## Portable Tools

### AST Context MCP Server

A standalone FastMCP server providing token-efficient AST parsing, skeleton extraction, and symbol isolation for Python and TypeScript/JavaScript. Enables agents to inspect large files without flooding the context window.

Four tools: `get_symbols`, `get_skeleton`, `get_symbol_block`, `get_hash`.

Works with any MCP-compatible agent client (Cursor, Claude Code, Antigravity).

→ [Full documentation](mcp_servers/ast_context_mcp/README.md)

### Context Benchmarking Harness

A deterministic simulation framework for evaluating agent context engineering strategies. Uses mock codebases with known-good solutions and a mock LLM pipeline to demonstrate the evaluation methodology.

→ [Full documentation](projects/context-benchmarking/README.md)

### AI Engineering Scaffold Plugin

The AI Engineering scaffold packaged for Antigravity, Claude Code (plugin marketplace or skill), Codex (skill), and GitHub Copilot (CLI extension + skill). It bundles synced copies of `bin/bootstrap_ai_engineering.sh`, the four reference guides, and the helper scripts. The canonical files stay in `bin/`, `docs/reference/`, and `scripts/`; `python3 scripts/sync_scaffold_plugin.py --check` (run by `pytest tests/`) fails if the plugin falls behind.

→ [Full documentation](plugins/ai-engineering-scaffold/README.md)

---

## Project Structure

```
hvr-agentic-os/
├── agent_app/                    # ADK multi-agent swarm (see agent_app/README.md)
├── plugins/                      # Shareable agent-harness plugins
│   └── ai-engineering-scaffold/  # Scaffold plugin (Antigravity, Claude, Codex, Copilot)
├── mcp_servers/                  # MCP tool servers
│   ├── ast_context_mcp/          # Standalone AST context server (portable)
│   ├── executor_mcp.py           # Workspace mutations (ADK-specific)
│   ├── auditor_mcp.py            # Staging promotion (ADK-specific)
│   └── ...
├── projects/                     # Standalone projects
│   └── context-benchmarking/     # Context engineering benchmark harness
├── docs/
│   ├── reference/                # Portable implementation guides ← START HERE
│   │   ├── llm-wiki-antigravity.md
│   │   ├── drift-registry.md
│   │   ├── session-workflows.md
│   │   └── elephant-goldfish-verification.md
│   ├── drift_registries/         # Cross-file dependency tracking (JSON)
│   └── retrospectives/           # Session retrospective archive
├── wiki/                         # LLM-maintained knowledge base
│   ├── entities/                 # Systems, tools, services
│   ├── concepts/                 # Patterns, principles, frameworks
│   └── synthesis/                # Cross-cutting analyses
├── scripts/                      # Utility scripts
│   ├── drift_enforcer.py         # Dependency drift detector
│   ├── wiki_db_init.py           # Postgres schema creator
│   ├── wiki_db_backfill.py       # Wiki → DB sync
│   └── sync_scaffold_plugin.py   # Canonical scaffold → plugin assets sync
├── bin/                          # Bootstrap and orchestration scripts
│   ├── bootstrap_ai_engineering.sh  # AI Engineering scaffold setup
│   └── bootstrap_agentic_os.sh     # ADK swarm setup
├── .agents/                      # Agent governance
│   ├── skills/                   # Specialized capability guides and slash commands
│   └── rules/                    # Behavioral constraints
└── GEMINI.md                     # Agent operational constitution
```

---

## Multi-Agent OS

The ADK multi-agent swarm is a complete zero-trust operating system for autonomous code generation. It's the system that the AI Engineering scaffold was built to support.

**[→ Full documentation in `agent_app/README.md`](agent_app/README.md)**

Includes: agent architecture, quick start, evaluation suite (11 adversarial tests), zero-trust enforcement layers, Era 5 benchmarks, and firewall customization.

---

## Further Reading

- **[Engineering with AI](https://hvrinformatics.com/blog/series/engineering-with-ai)** — Blog series covering the concepts behind the scaffold
- **[Meta-Retrospective](docs/retrospectives/2026-04-23_hvr_agentic_os_meta_retrospective.md)** — Complete project timeline
- **[Era 5 Conclusion](docs/retrospectives/2026-04-24_era_5_head_to_head_conclusion.md)** — Solo vs Swarm definitive analysis
- **[Tool Parallelism Analysis](docs/retrospectives/2026-04-25_tool_parallelism_bottleneck_analysis.md)** — Deepest architectural analysis

---

## License

MIT — see [LICENSE.md](LICENSE.md).
