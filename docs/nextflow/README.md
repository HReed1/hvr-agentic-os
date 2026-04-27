# Nextflow / nf-core Open-Source Contributions

Automated tooling and documentation for contributing to the [nf-core/modules](https://github.com/nf-core/modules) ecosystem, powered by the HVR Agentic OS swarm.

## Tools

### `stub_generator.py`
**Path:** [`tools/scripts/stub_generator.py`](tools/scripts/stub_generator.py)

An AST mutation engine that programmatically generates Nextflow `stub:` blocks for nf-core modules that are missing them. It:

1. Scans all `main.nf` files in a local `nf-core/modules` clone
2. Parses `output:` channel declarations to determine required stub files
3. Generates the correct stub command for each output type:
   - Plain-text → `touch ${prefix}.ext`
   - Compressed (`.gz`) → `echo | gzip > ${prefix}.ext.gz`
   - Index (`.tbi`) → `touch ${prefix}.ext.tbi`
4. Copies the `versions.yml` block 1:1 from the `script:` block for parity
5. Skips modules using `topic: versions` emit patterns (handled by Nextflow automatically)

**Usage:**
```python
import stub_generator as sg
sg.REPO_DIR = '/path/to/nf-core/modules'
sg.main()
```

### `process_modules.py`
**Path:** [`tools/scripts/process_modules.py`](tools/scripts/process_modules.py)

A module scanner that identifies nf-core modules with stub-related issues (e.g., `touch *.gz` anti-patterns, missing stub blocks). Used for analysis and reporting.

## Issues Tracked

| Issue | Description | Status | PR | Local Artifacts |
|---|---|---|---|---|
| [#5409](https://github.com/nf-core/modules/issues/5409) | Fix invalid `touch .gz` stubs → `echo \| gzip >` | ✅ [PR #11312](https://github.com/nf-core/modules/pull/11312) | Merged | [📂 issues/5409-fix-stub-gz/](issues/5409-fix-stub-gz/) |
| [#4570](https://github.com/nf-core/modules/issues/4570) | Add `stub:` blocks to all remaining modules | 🔧 In Progress | Pending | [📂 issues/4570-add-stub-blocks/](issues/4570-add-stub-blocks/) |

> Each issue directory contains the swarm-generated implementation plan, diffs, and validation reports. See [issues/](issues/) for the full index.

## Directory Structure

```
docs/nextflow/
├── reference/          # Standing reference docs (nf-core conventions, S3 analysis)
├── tools/              # Reusable scripts and tests
│   ├── scripts/        # stub_generator.py, process_modules.py
│   └── tests/          # Validation test suite
├── issues/             # Per-issue artifacts
│   ├── 5409-fix-stub-gz/
│   │   ├── implementation_plan.md
│   │   ├── directive.md
│   │   ├── reports/
│   │   └── diffs/
│   └── 4570-add-stub-blocks/
│       ├── implementation_plan.md
│       ├── full_migration.diff
│       └── swarm_architecture.md
└── walkthroughs/       # Retrospectives and learning docs
```

## Key Conventions

These conventions were established through maintainer feedback on PR #11312:

| Output Type | Stub Command | Rationale |
|---|---|---|
| Plain text (`.tsv`, `.txt`, `.fa`) | `touch ${prefix}.ext` | Creates empty placeholder |
| Compressed (`.gz`, `.fastq.gz`) | `echo \| gzip > ${prefix}.ext.gz` | Produces valid gzip header |
| Index files (`.tbi`, `.bai`) | `touch ${prefix}.ext.tbi` | Not actual gzip — `touch` is correct |
| Archives (`.zip`) | `touch ${prefix}.zip` | Placeholder only |
| `versions.yml` | Copy from `script:` block | Ensures 1:1 parity |
| `topic: versions` modules | Skip `versions.yml` | Nextflow handles automatically |

## Nextflow Stub Documentation

- **Official docs:** [nextflow.io/docs/latest/process.html#stub](https://www.nextflow.io/docs/latest/process.html#stub)
- **Trigger:** `nextflow run main.nf -stub-run`
- **Purpose:** Fast DAG validation without running real bioinformatics tools
- **Rule:** Stub must produce all files declared in `output:` — if it doesn't, the pipeline fails

## Contributing

New nf-core issues should be added as subdirectories under `issues/`:

```
issues/<issue-number>-<short-slug>/
├── implementation_plan.md
├── reports/
└── diffs/
```
