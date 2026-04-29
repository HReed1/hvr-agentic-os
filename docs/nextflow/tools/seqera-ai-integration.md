# Seqera AI × Antigravity/Gemini Integration

> First-ever cross-platform agent integration between Google's Antigravity/Gemini IDE and Seqera AI CLI

**Created**: 2026-04-29 | **Seqera AI CLI**: v1.5.0 | **Organization**: 2026-boston-summit

---

## Overview

This document describes the integration of [Seqera AI CLI](https://docs.seqera.io/platform-cloud/seqera-ai/) as a **domain-expert subagent** within the Antigravity/Gemini agentic IDE. Antigravity handles the full-stack software engineering workflow (GitHub PRs, CI/CD, AWS infrastructure, FinOps), while Seqera AI is invoked specifically for Nextflow-domain tasks where its specialized knowledge adds value.

This is a **manual adaptation** — Antigravity/Gemini is not yet in Seqera AI's officially supported agent list (Claude Code, Codex, Copilot, Cursor, OpenCode, Pi, Windsurf). We created the integration using the portable [Agent Skills](https://agentskills.io) convention.

## Architecture

```
┌──────────────────────────────────────────────────┐
│  Antigravity/Gemini IDE (Host Agent)             │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  MCP Tools                                 │  │
│  │  • GitHub MCP (PR management, reviews)     │  │
│  │  • AWS Batch Diagnostics (run triage)      │  │
│  │  • FinOps Oracle (cost analysis)           │  │
│  │  • TDAID AST Validation (test-driven dev)  │  │
│  │  • Postgres Local (database queries)       │  │
│  └────────────────────────────────────────────┘  │
│           │                                      │
│           ▼  run_command("seqera ai ...")         │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  Seqera AI CLI (Subagent)                  │  │
│  │  • Nextflow DSL2 expertise                 │  │
│  │  • nf-core module registry                 │  │
│  │  • Seqera Platform workspace API           │  │
│  │  • Wave container builds                   │  │
│  │  • LSP code intelligence                   │  │
│  │  • Built-in /slash command skills          │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## Setup

### Prerequisites
- Node.js 18+
- Seqera Platform account ([sign up](https://cloud.seqera.io))

### Installation
```bash
npm install -g seqera        # Install CLI
seqera login                  # Authenticate via browser OAuth
seqera org                    # Select organization
seqera --version              # Verify (expect >= 1.5.0)
```

### Skill File Location
The skill is installed at:
```
.agents/skills/seqera-ai-subagent/SKILL.md
```

This location is discovered by both Antigravity (via `.agents/skills/`) and Seqera AI itself (discovery priority 1).

## Invocation Patterns

### Headless Mode (Recommended)
Single-shot queries with plain-text output:
```bash
seqera ai --headless --approval-mode basic "<question>" 2>&1
```

### Sub-Agent Mode (Structured Output)
Machine-parseable JSONL for programmatic integration:
```bash
seqera ai --sub-agent --approval-mode basic "<question>" 2>&1
```

### Goal Mode (Autonomous Multi-Step)
For complex tasks requiring autonomous execution:
```bash
seqera ai --headless --approval-mode full "/goal <task>" 2>&1
```

### Approval Modes

| Mode | Flag | Use Case |
|---|---|---|
| **basic** | `--approval-mode basic` | Read-only queries, module search, analysis |
| **default** | *(no flag)* | Standard workspace file operations |
| **full** | `--approval-mode full` | Autonomous execution (use with `/goal`) |

## When to Delegate to Seqera AI

### ✅ Good Use Cases

| Task | Seqera AI Skill | Advantage |
|---|---|---|
| Pipeline structure analysis | `/nf-pipeline-structure` | Native DSL2 channel/process awareness |
| Platform run debugging | `/debug-last-run-on-seqera` | Direct workspace API access |
| Wave container builds | Natural language | No Dockerfile required |
| nf-core module discovery | Natural language | Built-in registry search |
| Nextflow config generation | `/nextflow-config` | Nextflow-native understanding |
| DSL2 syntax validation | `/fix-strict-syntax` | v2 parser migration |
| Schema generation | `/nextflow-schema` | JSON schema automation |

### ❌ Use Antigravity Instead

| Task | Antigravity Tool | Why |
|---|---|---|
| GitHub PR management | GitHub MCP | Seqera AI lacks GitHub API |
| AWS Batch diagnostics | `aws-batch-diagnostics` MCP | Custom infrastructure |
| FinOps cost analysis | `finops-infrastructure-oracle` MCP | Custom cost engine |
| TDAID test validation | `tdaid-ast-validation` MCP | Custom test framework |
| Frontend/React work | Antigravity native | Not Seqera AI's domain |

## Verified Example

Executed on 2026-04-29:
```bash
$ seqera ai --headless --approval-mode basic \
    "What nf-core modules are available for emm typing?"

Just one relevant result:

- nf-core/emmtyper — EMM typing of Streptococcus pyogenes assemblies
```

This correctly identified the `emmtyper` module — the same module we actively migrated in [PR #11377](https://github.com/nf-core/modules/pull/11377).

## Built-In Slash Commands

| Command | Purpose |
|---|---|
| `/nextflow-config` | Generate/explain Nextflow configuration |
| `/nextflow-schema` | Generate `nextflow_schema.json` and sample sheet schemas |
| `/debug-local-run` | Debug local run using `.nextflow.log` |
| `/debug-last-run-on-seqera` | Debug last Platform run |
| `/fix-strict-syntax` | Fix strict syntax / v2 parser migration |
| `/nf-pipeline-structure` | Analyze processes, workflows, channel flow |
| `/nf-run-history` | Analyze local run history |
| `/nf-schema-migration` | Migrate nf-validation → nf-schema v2 |
| `/seqera-mcp` | Access Platform through MCP tools |
| `/seqera-platform-api` | Query Platform via REST API |
| `/simplify` | Review code for quality and efficiency |

## Upstream Contribution Plan

This integration is a candidate for upstreaming to [`seqeralabs/docs`](https://github.com/seqeralabs/docs):

1. **New documentation page**: `skill-antigravity.md` following the pattern of existing `skill-claude-code.md`, `skill-codex.md`, etc.
2. **CLI enhancement request**: Add `.agents/skills/` and `GEMINI.md` as recognized targets in `seqera skill install`
3. **Agent Skills ecosystem**: Register at [agentskills.io](https://agentskills.io)

See: [Fork: seqeralabs/docs](/Users/harrisonreed/Projects/seqeralabs-docs/) *(local development)*

## References

- [SKILL.md](../../.agents/skills/seqera-ai-subagent/SKILL.md) — The Antigravity skill file
- [Seqera AI Documentation](https://docs.seqera.io/platform-cloud/seqera-ai/) — Official docs
- [Agent Skills Convention](https://agentskills.io) — Portable skill standard
- [PR #11377](https://github.com/nf-core/modules/pull/11377) — Pilot module migration using this workflow
