# Nextflow / nf-core Open-Source Contributions

Automated tooling and documentation for contributing to the [nf-core/modules](https://github.com/nf-core/modules) ecosystem, powered by the HVR Agentic OS swarm.

---

## Issues Tracked

| Issue | Description | Status | PR | Local Artifacts |
|---|---|---|---|---|
| [#5409](https://github.com/nf-core/modules/issues/5409) | Fix invalid `touch .gz` stubs → `echo \| gzip >` | ✅ [PR #11312](https://github.com/nf-core/modules/pull/11312) | Merged | [📂 issues/5409-fix-stub-gz/](issues/5409-fix-stub-gz/) |
| [#4570](https://github.com/nf-core/modules/issues/4570) | Add `stub:` blocks to all remaining modules | 🔧 [PR #11323](https://github.com/nf-core/modules/pull/11323) | Split into 10 PRs | [📂 issues/4570-add-stub-blocks/](issues/4570-add-stub-blocks/) |
| [#10832](https://github.com/nf-core/modules/issues/10832) | Migrate modules to topic channels | 🚀 [PR #11377](https://github.com/nf-core/modules/pull/11377) | Pilot (emmtyper) | [📂 issues/4570-add-stub-blocks/](issues/4570-add-stub-blocks/) |

---

## Document Index

### Issue #5409 — Fix Stub `.gz` Patterns

| Document | Description |
|---|---|
| [Implementation Plan](issues/5409-fix-stub-gz/implementation_plan.md) | Hackathon plan covering ingestion, triage, and fix strategy for `touch .gz` anti-pattern |
| [Director Directive](issues/5409-fix-stub-gz/directive.md) | ADK Web UI prompt used to launch the swarm for this issue |
| [Module Inventory](issues/5409-fix-stub-gz/reports/module_inventory.md) | Inventory of fixed modules and their PR mappings |
| [Diff Report](issues/5409-fix-stub-gz/reports/diff_report.md) | Per-module diff confidence, conditional logic, and scope assessment |
| [Validation Summary](issues/5409-fix-stub-gz/reports/validation.md) | Diff validation results for all modules in scope |

### Issue #4570 — Add Stub Blocks to All Modules

| Document | Description |
|---|---|
| [Implementation Plan](issues/4570-add-stub-blocks/implementation_plan.md) | Research and implementation strategy for adding stubs to 40 of 44 remaining modules |
| [PR Split Strategy](issues/4570-add-stub-blocks/pr_split_strategy.md) | 10-branch split plan per reviewer feedback, including design patterns and anti-patterns |
| [Validation Report](issues/4570-add-stub-blocks/validation_report.md) | Full test results for all 40 modules across Phase 1 and Phase 2 |
| [Swarm Architecture](issues/4570-add-stub-blocks/swarm_architecture.md) | Technical case study of how the agentic swarm executed this contribution autonomously |
| [Archived Diffs](hackathon/diffs_issue_11323/) | 10 category-based diff files for each split PR branch |

### Reference

| Document | Description |
|---|---|
| [nf-core Contributing Reference](reference/nfcore_contributing_reference.md) | Internalized reference of nf-core contributing and developing conventions |
| [Bucket Analysis](reference/BUCKET_ANALYSIS.md) | Scope analysis splitting 101 swarm-generated diffs into in-scope vs. out-of-scope buckets |

### Tools & Integrations

| Document | Description |
|---|---|
| [Seqera AI Integration](tools/seqera-ai-integration.md) | First-ever Antigravity/Gemini × Seqera AI CLI cross-agent integration |

### Walkthroughs

| Document | Description |
|---|---|
| [Hackathon Breakdown](walkthroughs/hackathon_breakdown_walkthrough.md) | Ingestion and triage walkthrough for the 739-item hackathon project board |
| [Hackathon Issues Plan](walkthroughs/nextflow_hackathon_issues_implementation_plan.md) | Autonomous issue ingestion and triage implementation plan |
| [Bug Fix Post-Mortem](walkthroughs/4_bug_nextflow_fix_walkthrough.md) | Post-mortem analysis of session `317dde31` |
| [Emmtyper Pilot Retrospective](walkthroughs/2026-04-29_emmtyper_pilot_retrospective.md) | PR #11377 lessons learned: 5 pushes to green, pre-push checklist, module migration template |

---

## Key Conventions

These conventions were established through maintainer feedback on [PR #11312](https://github.com/nf-core/modules/pull/11312), [PR #11349](https://github.com/nf-core/modules/pull/11349), and [PR #11377](https://github.com/nf-core/modules/pull/11377):

### Stub Output Patterns

| Output Type | Stub Command | Rationale |
|---|---|---|
| Plain text (`.tsv`, `.txt`, `.fa`) | `touch ${prefix}.ext` | Creates empty placeholder |
| Compressed (`.gz`, `.fastq.gz`) | `echo \| gzip > ${prefix}.ext.gz` | Produces valid gzip header ([reviewer ref](https://github.com/nf-core/modules/pull/11312#discussion_r3146198459)) |
| Index files (`.tbi`, `.bai`) | `touch ${prefix}.ext.tbi` | Not actual gzip — `touch` is correct |
| Archives (`.zip`) | `touch ${prefix}.zip` | Placeholder only |
| `versions.yml` | Copy from `script:` block | Ensures 1:1 parity |
| `topic: versions` modules | Skip `versions.yml` | Nextflow handles automatically |

> [!IMPORTANT]
> Use `echo | gzip >` (no quotes, no arguments). **NOT** `echo "" | gzip >` or `echo '' | gzip >`.
> See [PR #11312 reviewer discussion](https://github.com/nf-core/modules/pull/11312#discussion_r3146198459).

### Topic Channel `eval()` Pattern

When migrating a module to `topic: versions`, the `eval()` string **must** use single quotes to prevent Groovy interpolation and avoid Conda bash syntax errors:

```nextflow
// ✅ CORRECT — single-quoted eval, direct pipe, double-quoted sed
tuple val("${task.process}"), val('toolname'), eval('toolname --version 2>&1 | sed "s/^.*toolname v//"'), topic: versions, emit: versions_toolname

// ✅ PREFERRED for Python/Click tools — immune to Click version format differences
tuple val("${task.process}"), val('toolname'), eval('python -c "import toolname; print(toolname.__version__)"'), topic: versions, emit: versions_toolname

// ❌ WRONG — double-quoted eval, echo $() wrapper (breaks Conda CI)
tuple val("${task.process}"), val('toolname'), eval("echo \$(toolname --version 2>&1) | sed 's/^.*toolname v//'"), topic: versions, emit: versions_toolname
```

> [!CAUTION]
> The `echo $()` wrapper captures Python tracebacks from tools like emmtyper. Parentheses in tracebacks cause `bash: syntax error near unexpected token '('`. Always pipe directly without `echo $()`.

> [!TIP]
> For **Python/Click-based tools**, prefer `python -c "import pkg; print(pkg.__version__)"` over `--version | sed`. Click's output format differs between versions (Click 7: `tool v1.0` vs Click 8: `tool, version 1.0`), causing Conda CI failures when the sed pattern doesn't match.

Canonical references:
- `modules/nf-core/shapeit5/phasecommon/main.nf` (sed pattern)
- `modules/nf-core/emmtyper/main.nf` (python import pattern, PR #11377)

### Test Snapshot Convention

Always use `sanitizeOutput()` from [nf-core/nft-utils](https://github.com/nf-core/nft-utils) to clean up snapshots:

```groovy
// ✅ CORRECT
{ assert snapshot(sanitizeOutput(process.out)).match() }

// ❌ WRONG — raw process.out creates brittle, hard-to-read snapshots
{ assert snapshot(process.out).match() }
```

Source: [PR #11349 reviewer feedback](https://github.com/nf-core/modules/pull/11349#discussion_r3162160283) (famosab).

### PR Strategy

Every module PR must be a complete, self-contained unit:
1. **Topic channel migration** — `eval()` output with `topic: versions`
2. **Stub block** — `stub:` section in `main.nf`
3. **Tests with `sanitizeOutput()`** — Both regular and `-stub` test cases
4. **1 module per PR** — Atomic, independently reviewable
5. **`meta.yml` auto-generated** — Always run `nf-core modules lint --fix` (never hand-edit `meta.yml`)

### Local Validation Checklist (Pre-Push)

> [!IMPORTANT]
> Every module PR must pass **ALL** of these locally before pushing. Failure to run this checklist caused 4 of our 5 CI failures on the emmtyper pilot.

```bash
# 1. Auto-fix meta.yml from main.nf (ALWAYS run this — meta.yml is a derived artifact)
nf-core modules lint <module> --fix

# 2. Restore EDAM ontology comments (lint --fix strips YAML comments)
docs/nextflow/tools/scripts/restore_edam_comments.sh <module>

# 3. Lint (must be 0 failures, 0 warnings)
nf-core modules lint <module>

# 4. Prettier (must match CI's formatter — catches YAML quoting issues)
npx prettier --check modules/nf-core/<module>/meta.yml

# 5. Tests (must pass and produce stable snapshots)
nf-core modules test <module> --update --profile docker

# 6. Seqera AI structural review (optional but catches non-obvious issues)
seqera ai --headless --approval-mode basic \
  "Review modules/nf-core/<module>/main.nf for topic channel, stub, and eval correctness"
```

### Seqera AI as QA Gate

The [Seqera AI integration](tools/seqera-ai-integration.md) provides domain-expert validation that complements linting:
- Validates `eval()` quoting and `topic:`/`emit:` ordering
- Catches semantic issues (e.g., wrong test data organism)
- Recommends robust version extraction patterns (e.g., `python -c import` for Click tools)
- See PR #11377 for the first validated use case

---

## Directory Structure

```
docs/nextflow/
├── README.md                    # ← This file
├── reference/                   # Standing reference docs
│   ├── nfcore_contributing_reference.md
│   └── BUCKET_ANALYSIS.md
├── issues/                      # Per-issue artifacts
│   ├── 5409-fix-stub-gz/
│   │   ├── implementation_plan.md
│   │   ├── directive.md
│   │   └── reports/
│   │       ├── module_inventory.md
│   │       ├── diff_report.md
│   │       └── validation.md
│   └── 4570-add-stub-blocks/
│       ├── implementation_plan.md
│       ├── pr_split_strategy.md
│       ├── validation_report.md
│       └── swarm_architecture.md
├── tools/
│   ├── scripts/
│   ├── tests/
│   └── seqera-ai-integration.md  # Seqera AI × Antigravity integration
└── walkthroughs/                # Retrospectives and learning docs
    ├── hackathon_breakdown_walkthrough.md
    ├── nextflow_hackathon_issues_implementation_plan.md
    └── 4_bug_nextflow_fix_walkthrough.md
```
