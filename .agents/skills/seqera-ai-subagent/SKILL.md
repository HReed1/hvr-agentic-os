---
name: seqera-ai-subagent
description: Invokes the Seqera AI CLI as a domain-expert subagent for Nextflow pipeline development, nf-core module management, Seqera Platform workspace operations, and Wave container builds. This is the first Antigravity/Gemini integration with Seqera AI.
---

# Seqera AI Subagent Integration for Antigravity/Gemini

Seqera AI (`seqera ai`) is a domain-specific CLI coding assistant built by Seqera for Nextflow and bioinformatics workflows. This skill enables Antigravity to delegate Nextflow-specific tasks to Seqera AI, which has deep built-in awareness of Nextflow DSL2, nf-core, Seqera Platform, and Wave containers.

## Prerequisites

- `seqera` CLI installed globally: `npm install -g seqera`
- Authenticated: `seqera login`
- Organization selected: `seqera org` (current: `2026-boston-summit`)

Verify readiness:
```bash
seqera --version  # Expect >= 1.5.0
seqera org         # Confirm active organization
```

## When to Use This Skill

Delegate to Seqera AI when the task involves:

| Task Category | Examples | Seqera AI Advantage |
|---|---|---|
| **Pipeline structure analysis** | Analyze channel flow, process topology, DAG dependencies | Native DSL2 understanding, `/nf-pipeline-structure` |
| **Platform run debugging** | Inspect failed runs, view task logs, check metrics | Direct Platform API access via authenticated workspace |
| **Wave container builds** | Create ad-hoc containers with conda/pip packages | On-the-fly container synthesis without Dockerfiles |
| **nf-core module discovery** | Search for modules, get usage examples, check compatibility | Built-in nf-core registry search |
| **Nextflow config generation** | Generate or validate `nextflow.config` for specific profiles | Nextflow-native config awareness |
| **DSL2 syntax validation** | Fix strict syntax errors, migrate v1 → v2 parser | `/fix-strict-syntax` built-in skill |
| **Schema generation** | Generate `nextflow_schema.json` or sample sheet schemas | `/nextflow-schema` built-in skill |
| **Platform operations** | Launch pipelines, manage datasets, view compute environments | `/seqera-platform-api`, `/seqera-mcp` |

**Do NOT delegate** when the task involves:
- GitHub PR management (use GitHub MCP)
- AWS Batch diagnostics for self-managed infrastructure (use `aws-batch-diagnostics` MCP)
- FinOps cost analysis (use `finops-infrastructure-oracle` MCP)
- TDAID test-driven validation (use `tdaid-ast-validation` MCP)
- Frontend/React development (not Seqera AI's domain)

## Invocation Patterns

### Pattern 1: Headless Query (Recommended)
For single-shot queries that return structured text output:

```bash
seqera ai --headless --approval-mode basic "<your question>" 2>&1
```

Example:
```bash
seqera ai --headless --approval-mode basic "Search nf-core modules for a tool that performs emm typing on Streptococcus assemblies" 2>&1
```

### Pattern 2: Sub-Agent Mode (Structured JSONL)
For programmatic integration requiring structured, machine-parseable output:

```bash
seqera ai --sub-agent --approval-mode basic "<your question>" 2>&1
```

This outputs structured JSONL events that can be parsed programmatically.

### Pattern 3: Headless Goal-Directed Execution
For multi-step tasks where Seqera AI should work autonomously:

```bash
seqera ai --headless --approval-mode full "/goal <task description>" 2>&1
```

Example:
```bash
seqera ai --headless --approval-mode full "/goal Analyze the pipeline structure of src/pipelines/main.nf and report all process dependencies" 2>&1
```

### Pattern 4: Built-In Skill Invocation
For specific built-in capabilities:

```bash
seqera ai --headless --approval-mode basic "/<skill-name> <context>" 2>&1
```

Available built-in skills:

| Slash Command | Purpose |
|---|---|
| `/nextflow-config` | Generate/explain Nextflow configuration |
| `/nextflow-schema` | Generate `nextflow_schema.json` and sample sheet schemas |
| `/debug-local-run` | Debug local Nextflow run using `.nextflow.log` |
| `/debug-last-run-on-seqera` | Debug last Platform run |
| `/fix-strict-syntax` | Fix strict syntax / v2 parser migration |
| `/nf-pipeline-structure` | Analyze pipeline processes, workflows, channel flow |
| `/nf-run-history` | Analyze local Nextflow run history |
| `/nf-schema-migration` | Migrate nf-validation → nf-schema v2 |
| `/seqera-mcp` | Access Platform through MCP tools |
| `/seqera-platform-api` | Query Platform resources via REST API |
| `/simplify` | Review code for reuse, quality, efficiency |

### Pattern 5: Wave Container Build
For rapid container prototyping without Docker/ECR:

```bash
seqera ai --headless --approval-mode full "Build a Wave container with conda packages: bwa=0.7.17, samtools=1.17, python=3.11" 2>&1
```

### Pattern 6: Module QA Review (Validated in PR #11377)

Pre-push structural review of an nf-core module. Catches issues that `nf-core lint` misses:

```bash
seqera ai --headless --approval-mode basic \
  "Review modules/nf-core/<module>/main.nf for topic channel, stub, and eval correctness. Check: 1) eval() uses single quotes, 2) topic: versions before emit:, 3) stub block exists, 4) version extraction is robust for both Docker and Conda." 2>&1
```

**Validated catches from the emmtyper pilot:**
- Recommended `python -c "import emmtyper; print(emmtyper.__version__)"` over fragile `--version | sed` pattern
- Identified that Click-based tools have version format differences between Click 7 and Click 8
- Confirmed stub output patterns and topic channel ordering

### Pattern 7: Session Continuation
Resume a previous Seqera AI session:

```bash
seqera ai -c  # Continue most recent session
seqera ai -s <session-id>  # Resume specific session
```

## Approval Modes

When invoking Seqera AI as a subagent, choose the appropriate approval mode:

| Mode | Flag | When to Use |
|---|---|---|
| **basic** | `--approval-mode basic` | Read-only queries, analysis, search |
| **default** | (no flag) | Standard workspace file operations |
| **full** | `--approval-mode full` | Autonomous multi-step execution (use with `/goal`) |

## Architecture: How This Integration Works

```
┌─────────────────────────────────────┐
│  Antigravity/Gemini (Host Agent)    │
│  ┌──────────────────────────────┐   │
│  │  MCP Tools (AWS, GitHub,     │   │
│  │  FinOps, TDAID, Postgres)    │   │
│  └──────────────────────────────┘   │
│           │                         │
│           ▼                         │
│  run_command("seqera ai ...")       │
│           │                         │
│           ▼                         │
│  ┌──────────────────────────────┐   │
│  │  Seqera AI CLI (Subagent)    │   │
│  │  - Nextflow DSL2 expertise   │   │
│  │  - nf-core registry          │   │
│  │  - Platform workspace API    │   │
│  │  - Wave container builds     │   │
│  │  - LSP code intelligence     │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

Antigravity orchestrates the overall workflow (GitHub PRs, CI/CD, infrastructure, cost analysis), and delegates Nextflow-domain tasks to Seqera AI when its specialized knowledge adds value.

## Security Constraints

1. **Never pass secrets** to Seqera AI via command-line arguments. Seqera AI manages its own authentication via `seqera login`.
2. **Approval mode**: Default to `basic` for read-only operations. Only use `full` when autonomous execution is explicitly needed.
3. **Workspace isolation**: Seqera AI operates within its authenticated workspace scope. It cannot access resources outside the selected organization.
4. **Output capture**: Always pipe output through `head -N` or `tail -N` to prevent overwhelming context windows with verbose Nextflow logs.

## Credit Usage

Seqera Cloud users have credit-based pricing. Each Seqera AI invocation consumes credits based on the complexity of the request. Monitor usage at [cloud.seqera.io](https://cloud.seqera.io).

> **Current allocation**: $20 free credits + additional summit credits (2026-boston-summit organization).

## Advanced CLI Flags

For debugging and observability, the following flags enhance headless/sub-agent output:

| Flag | Purpose |
|---|---|
| `--show-thinking` | Display model reasoning in headless mode |
| `--show-tools` | Show tool calls in headless mode |
| `--show-tool-results` | Show tool results in headless mode |
| `--events-path <file>` | Write all events as JSONL to a file for post-hoc analysis |

Example with full observability:
```bash
seqera ai --headless --show-tools --show-tool-results --approval-mode basic "What version of emmtyper is available in nf-core modules?" 2>&1
```

## Verified Smoke Test

The following query was successfully executed on **2026-04-29** to validate the integration:

```bash
$ seqera ai --headless --approval-mode basic \
    "What nf-core modules are available for emm typing? Just list module names briefly." 2>&1
```

**Response:**
```
Just one relevant result:

- **nf-core/emmtyper** — EMM typing of Streptococcus pyogenes assemblies
```

✅ Seqera AI correctly identified the `emmtyper` module — the same module we are actively migrating in our nf-core contribution work (PR #11377).

## Compatibility Note

This skill represents the **first manual adaptation** of Seqera AI for the Antigravity/Gemini agent platform. The official `seqera skill install` command currently supports: Claude Code, Codex, GitHub Copilot, Cursor, OpenCode, Pi, and Windsurf.

This adaptation follows the [Agent Skills](https://agentskills.io) convention used by `.agents/skills/` discovery directories, making it portable across any agent that supports this standard.

**Contribution opportunity**: This integration pattern can be proposed upstream to Seqera as a new supported agent target via a fork of `seqeralabs/docs`.
