# HVR Agentic OS

> 📰 **As seen on [HVRInformatics.com](https://hvrinformatics.com/blog)**

A Zero-Trust multi-agent operating system built on [Google's Agent Development Kit (ADK)](https://google.github.io/adk-docs/), and a portable **AI Engineering scaffold** for structuring how LLM agents maintain knowledge, track dependencies, and work across sessions.

---

## What's In This Repo

**Two things:**

1. **A Multi-Agent Swarm** — Four specialized AI agents (Director, Executor, QA Engineer, Auditor) collaborating through strict tool segregation, adversarial verification, and DLP-enforced sandbox boundaries. → [See `agent_app/README.md`](agent_app/README.md)

2. **A Portable AI Engineering Scaffold** — Battle-tested patterns for LLM-maintained knowledge bases, cross-file dependency tracking, and structured session workflows. These work with any LLM agent (Antigravity, Cursor, Claude Code, etc.) and can be adopted into any codebase. → Keep reading.

---

## AI Engineering Scaffold

The patterns below solve three problems that every LLM-assisted codebase eventually hits:

| Problem | Solution | Reference Guide |
|---------|----------|----------------|
| Knowledge evaporates between sessions | **LLM Wiki** — persistent, agent-maintained knowledge base | [llm-wiki-antigravity.md](docs/reference/llm-wiki-antigravity.md) |
| File changes silently break contracts | **Drift Registry** — machine-readable dependency tracking | [drift-registry.md](docs/reference/drift-registry.md) |
| Sessions start cold and end without trace | **Session Workflows** — structured open→work→close lifecycle | [session-workflows.md](docs/reference/session-workflows.md) |

These three systems reinforce each other. The wiki accumulates knowledge, the drift registry protects it from silent breakage, and the session workflows ensure both are maintained at every session boundary.

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
- An LLM agent (Antigravity, Cursor, Claude Code, etc.)

### 1. Bootstrap the Scaffold

```bash
chmod +x bin/bootstrap_ai_engineering.sh
./bin/bootstrap_ai_engineering.sh
```

This creates:
- `wiki/` — Directory structure for the LLM-maintained knowledge base
- `docs/drift_registries/` — Empty registry templates
- `docs/retrospectives/` — Session retrospective archive
- `.agents/` — Agent governance (skills, workflows, rules)
- `scripts/` — Utility scripts (drift enforcer)

The script is idempotent — run it multiple times safely.

### 2. Feed the Reference Guides to Your LLM

The bootstrap script prints an **LLM Ingest Prompt** at the end. Copy it and paste it into your LLM agent. It instructs the agent to read and implement the three reference guides in order:

1. **[LLM Wiki](docs/reference/llm-wiki-antigravity.md)** — Sets up wiki conventions, page templates, ingest/query/lint workflows, and (optionally) the Postgres metadata index
2. **[Drift Registry](docs/reference/drift-registry.md)** — Sets up dependency tracking, the enforcer script, and registry schemas
3. **[Session Workflows](docs/reference/session-workflows.md)** — Sets up `/session-start` and `/session-wrapup` workflows that tie the wiki and drift registry together

After ingestion, your agent will have created the `GEMINI.md` rules (or equivalent agent instructions), workflow files, and governance structure for your project.

### 3. Initialize the Wiki Database (Optional)

If you have PostgreSQL available and want the metadata index:

```bash
python3 scripts/wiki_db_init.py
```

This creates the `wiki` database with tables for page metadata, cross-references, and activity logging. The wiki works without the database (it's just markdown files), but the database enables fast SQL queries across all pages.

### 4. Start Your First Session

Tell your LLM agent:

```
/session-start
```

The agent will load the wiki overview, check for outstanding work, run the drift enforcer, and ask you for your session focus. When you're done:

```
/session-wrapup
```

The agent commits your work, enforces drift checks, generates a retrospective, and optionally ingests significant findings into the wiki.

---

## Adopting the Scaffold in Your Own Repos

The AI Engineering scaffold is designed to be portable. To adopt it in another repository:

1. **Copy the reference guides** — Place the three files from `docs/reference/` into your target repo
2. **Copy the bootstrap script** — Place `bin/bootstrap_ai_engineering.sh` in your target repo
3. **Copy the drift enforcer** — Place `scripts/drift_enforcer.py` in your target repo
4. **Run the bootstrap** — Execute the script, then feed the ingest prompt to your LLM agent
5. **Start working** — Use `/session-start` and `/session-wrapup` to structure your sessions

The agent handles everything else: creating the wiki, setting up registries, writing governance rules, and maintaining the knowledge base as you work.

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

---

## Project Structure

```
hvr-agentic-os/
├── agent_app/                    # ADK multi-agent swarm (see agent_app/README.md)
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
│   │   └── session-workflows.md
│   ├── drift_registries/         # Cross-file dependency tracking (JSON)
│   └── retrospectives/           # Session retrospective archive
├── wiki/                         # LLM-maintained knowledge base
│   ├── entities/                 # Systems, tools, services
│   ├── concepts/                 # Patterns, principles, frameworks
│   └── synthesis/                # Cross-cutting analyses
├── scripts/                      # Utility scripts
│   ├── drift_enforcer.py         # Dependency drift detector
│   ├── wiki_db_init.py           # Postgres schema creator
│   └── wiki_db_backfill.py       # Wiki → DB sync
├── bin/                          # Bootstrap and orchestration scripts
│   ├── bootstrap_ai_engineering.sh  # AI Engineering scaffold setup
│   └── bootstrap_agentic_os.sh     # ADK swarm setup
├── .agents/                      # Agent governance
│   ├── skills/                   # Specialized capability guides
│   ├── workflows/                # Session and operational workflows
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
