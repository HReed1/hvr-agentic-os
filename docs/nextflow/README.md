# Nextflow / nf-core Open-Source Contributions

Automated tooling and documentation for contributing to the [nf-core/modules](https://github.com/nf-core/modules) ecosystem, powered by the HVR Agentic OS swarm.

---

## Issues Tracked

| Issue | Description | Status | PR | Local Artifacts |
|---|---|---|---|---|
| [#5409](https://github.com/nf-core/modules/issues/5409) | Fix invalid `touch .gz` stubs → `echo \| gzip >` | ✅ [PR #11312](https://github.com/nf-core/modules/pull/11312) | Merged | [📂 issues/5409-fix-stub-gz/](issues/5409-fix-stub-gz/) |
| [#4570](https://github.com/nf-core/modules/issues/4570) | Add `stub:` blocks to all remaining modules | 🔧 [PR #11323](https://github.com/nf-core/modules/pull/11323) | Split into 10 PRs | [📂 issues/4570-add-stub-blocks/](issues/4570-add-stub-blocks/) |

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
| [Implementation Plan](issues/4570-add-stub-blocks/implementation_plan.md) | Research and implementation strategy for adding stubs to 44 remaining modules |
| [PR Split Strategy](issues/4570-add-stub-blocks/pr_split_strategy.md) | 10-branch split plan per reviewer feedback, including design patterns and anti-patterns |
| [Validation Report](issues/4570-add-stub-blocks/validation_report.md) | Full test results for all 40 modules across Phase 1 and Phase 2 |
| [Swarm Architecture](issues/4570-add-stub-blocks/swarm_architecture.md) | Technical case study of how the agentic swarm executed this contribution autonomously |
| [Archived Diffs](hackathon/diffs_issue_11323/) | 10 category-based diff files for each split PR branch |

### Reference

| Document | Description |
|---|---|
| [nf-core Contributing Reference](reference/nfcore_contributing_reference.md) | Internalized reference of nf-core contributing and developing conventions |
| [Bucket Analysis](reference/BUCKET_ANALYSIS.md) | Scope analysis splitting 101 swarm-generated diffs into in-scope vs. out-of-scope buckets |

### Walkthroughs

| Document | Description |
|---|---|
| [Hackathon Breakdown](walkthroughs/hackathon_breakdown_walkthrough.md) | Ingestion and triage walkthrough for the 739-item hackathon project board |
| [Hackathon Issues Plan](walkthroughs/nextflow_hackathon_issues_implementation_plan.md) | Autonomous issue ingestion and triage implementation plan |
| [Bug Fix Post-Mortem](walkthroughs/4_bug_nextflow_fix_walkthrough.md) | Post-mortem analysis of session `317dde31` |

---

## Key Conventions

These conventions were established through maintainer feedback on [PR #11312](https://github.com/nf-core/modules/pull/11312):

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
├── hackathon/
│   └── diffs_issue_11323/       # 10 archived PR diffs
└── walkthroughs/                # Retrospectives and learning docs
    ├── hackathon_breakdown_walkthrough.md
    ├── nextflow_hackathon_issues_implementation_plan.md
    └── 4_bug_nextflow_fix_walkthrough.md
```
