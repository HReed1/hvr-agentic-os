# Retrospective: Seqera AI Integration & nf-core Emmtyper Pilot PR

**Date**: 2026-04-29
**Scope**: Cross-agent Seqera AI integration, nf-core PR hardening, documentation codification
**Repositories Updated**: `ngs-variant-validator`, `hvr-agentic-os`, `seqeralabs-docs` (fork), `nf-core-modules` (fork)
**PR**: [nf-core/modules#11377](https://github.com/nf-core/modules/pull/11377) — emmtyper stub + topic channels

---

## Executive Summary

This session accomplished three major milestones:

1. **Stabilized the emmtyper pilot PR** (#11377) through 6 pushes, resolving all CI failures and reviewer feedback from maintainers @famosab, @SPPearce, and @mribeirodantas.
2. **Established the first-ever Seqera AI × Antigravity/Gemini cross-agent integration**, creating the skill, upstream documentation, and validated invocation patterns.
3. **Codified all lessons** into docs, workflows, skills, and automation scripts across 4 repositories to prevent regression on the remaining 39 module PRs.

---

## Phase 1: Seqera AI Skill Integration

### What We Built
Created [`.agents/skills/seqera-ai-subagent/SKILL.md`](../../.agents/skills/seqera-ai-subagent/SKILL.md) — the first manual adaptation of Seqera AI for the Antigravity/Gemini agent platform.

**Key design decisions:**
- Shell-based invocation via `run_command` → `seqera ai --headless` rather than MCP integration
- No custom MCP tools needed — Seqera AI is self-contained with its own CLI and authentication
- Seven invocation patterns documented: headless query, sub-agent mode, goal mode, built-in skills, Wave containers, module QA review, and session continuation

### Upstream Contribution
Created the upstream Seqera docs page at [`seqeralabs-docs/platform-cloud/docs/seqera-ai/skill-antigravity.md`](https://github.com/HReed1/docs/blob/feat/skill-antigravity-gemini/platform-cloud/docs/seqera-ai/skill-antigravity.md) covering:
- Skill format and installation instructions for Antigravity
- Invocation patterns table
- Validated use case: nf-core module QA

**Commits:**
```
ngs-variant-validator (ngs_nf_hack):
  bf1dea7 feat: Add Seqera AI subagent skill for Antigravity/Gemini
  991b981 docs: Add Seqera AI integration documentation to nextflow docs

seqeralabs-docs (feat/skill-antigravity-gemini):
  96ce16d7 docs: Add Antigravity/Gemini as a supported agent for Seqera AI skills
  90d45cb0 docs(skill-antigravity): Add Module QA Review pattern and validated use case
```

### Relevant Artifacts
- Skill: [`.agents/skills/seqera-ai-subagent/SKILL.md`](../../.agents/skills/seqera-ai-subagent/SKILL.md)
- Docs: [`docs/nextflow/tools/seqera-ai-integration.md`](../nextflow/tools/seqera-ai-integration.md)

---

## Phase 2: Emmtyper PR Stabilization (6 Pushes to Green)

### Timeline

| Push | Commit | CI Result | Issue | Fix |
|---|---|---|---|---|
| 1 | `1eb9d9c` | ❌ Snapshot mismatch | Initial submission with stale snapshots | Topic migration + stub + tests |
| 2 | `8a9d392` | ❌ eval() crash | Regenerated snapshots but eval still broken | `--update` regeneration |
| 3 | `05ac16e` | ❌ meta.yml desync | Single-quoted eval, added sanitizeOutput | Fixed main.nf, missed meta.yml |
| 4 | `150c555` | ❌ Prettier failed | Updated meta.yml to match main.nf | YAML quoting still wrong for prettier |
| 5 | `90b5a23` | ✅ All green | `python -c import` + prettier-compliant quotes | Robust version extraction |
| 6 | `755bed0` | ✅ Green (reviewer fix) | EDAM comment stripped by lint --fix | Restored `# TSV` comment |

### Root Causes Identified

#### Issue 1: `eval()` Quoting (Conda CI Crash)
The `echo $()` wrapper captured Python/Click tracebacks containing parentheses. Bash interpreted `(` as syntax.

```groovy
// BROKEN — crashes in Conda
eval("echo \$(emmtyper --version 2>&1 | sed 's/emmtyper v//')")

// FIXED — robust across Docker and Conda
eval('python -c "import emmtyper; print(emmtyper.__version__)"')
```

#### Issue 2: `sanitizeOutput()` Missing
Topic channels inject volatile version tuples into `process.out`. Without `sanitizeOutput()`, snapshots contain unstable numbered keys.

```groovy
// BROKEN
snapshot(process.out)

// FIXED
snapshot(sanitizeOutput(process.out))
```

#### Issue 3: `meta.yml` Out of Sync
`meta.yml` has its own copy of the eval expression. Fixing `main.nf` alone is insufficient — `nf-core modules lint --fix` must regenerate it.

#### Issue 4: Prettier Formatting
YAML double-quote escaping (`\"`) doesn't match prettier's normalization. Solution: always use `lint --fix` which produces prettier-compatible output.

#### Issue 5: Click Version Fragility
Click 7 writes `emmtyper v0.2.0` to stderr. Click 8 writes `emmtyper, version 0.2.0` to stdout. The `python -c import` pattern works identically in both.

#### Issue 6: EDAM Ontology Comments
`nf-core modules lint --fix` strips YAML inline comments (e.g., `# TSV`) during serialization because YAML comments aren't part of the data model. 1,055+ modules in the repo use these comments.

---

## Phase 3: Automation & Tooling

### `restore_edam_comments.sh`
Created [`docs/nextflow/tools/scripts/restore_edam_comments.sh`](../nextflow/tools/scripts/restore_edam_comments.sh) to automatically restore EDAM ontology comments stripped by `lint --fix`.

```bash
# How it works:
# 1. Reads upstream/master version of meta.yml
# 2. Finds EDAM lines with inline comments (e.g., "# TSV")
# 3. Checks if local file lost those comments
# 4. Restores them automatically

$ restore_edam_comments.sh emmtyper
RESTORED: http://edamontology.org/format_3475 # TSV
RESTORED: 1 EDAM comment(s) in modules/nf-core/emmtyper/meta.yml
```

### 6-Step Pre-Push Checklist (Validated)
Codified in [`docs/nextflow/README.md`](../nextflow/README.md) and [`.agents/nf-core-contribution.md`](../../.agents/nf-core-contribution.md):

```bash
# 1. Auto-fix meta.yml from main.nf
nf-core modules lint <module> --fix

# 2. Restore EDAM ontology comments
restore_edam_comments.sh <module>

# 3. Lint (must be 0 failures)
nf-core modules lint <module>

# 4. Prettier (must match CI formatter)
npx prettier --check modules/nf-core/<module>/meta.yml

# 5. Tests (must pass and produce stable snapshots)
nf-core modules test <module> --update --profile docker

# 6. Seqera AI structural review (optional)
seqera ai --headless --approval-mode basic \
  "Review modules/nf-core/<module>/main.nf for correctness"
```

---

## Phase 4: Documentation Propagation

### Anti-Patterns Codified (11 total, 6 new today)

| # | Anti-Pattern | Source |
|---|---|---|
| 6 | `meta.yml` is auto-generated — never hand-edit | PR #11377, push 3 |
| 7 | Always run `lint --fix` after changing `main.nf` | PR #11377, push 3 |
| 8 | All test snapshots must use `sanitizeOutput()` | Reviewer feedback (famosab) |
| 9 | Use `python -c import` for Python/Click tools | Seqera AI recommendation |
| 10 | Run `npx prettier --check` before pushing | PR #11377, push 5 |
| 11 | Run `restore_edam_comments.sh` after `lint --fix` | Reviewer feedback (mribeirodantas) |

### Files Updated Across All Repos

| File | Repo | Changes |
|---|---|---|
| [`docs/nextflow/README.md`](../nextflow/README.md) | Both | Topic channel conventions, Python import pattern, 6-step checklist, Seqera AI QA |
| [`docs/nextflow/tools/seqera-ai-integration.md`](../nextflow/tools/seqera-ai-integration.md) | Both | Full Seqera AI × Antigravity integration guide |
| [`docs/nextflow/tools/scripts/restore_edam_comments.sh`](../nextflow/tools/scripts/restore_edam_comments.sh) | Both | EDAM comment restoration script |
| [`docs/nextflow/walkthroughs/2026-04-29_emmtyper_pilot_retrospective.md`](../nextflow/walkthroughs/2026-04-29_emmtyper_pilot_retrospective.md) | Both | Full PR post-mortem with migration template |
| [`docs/nextflow/issues/4570-add-stub-blocks/pr_split_strategy.md`](../nextflow/issues/4570-add-stub-blocks/pr_split_strategy.md) | Both | Updated anti-patterns, superseded PRs note |
| [`.agents/skills/seqera-ai-subagent/SKILL.md`](../../.agents/skills/seqera-ai-subagent/SKILL.md) | Both | New skill (7 invocation patterns) |
| [`.agents/nf-core-contribution.md`](../../.agents/nf-core-contribution.md) | Both | 6 new anti-patterns, pre-push checklist |
| `skill-antigravity.md` | seqeralabs-docs | Upstream Seqera docs for Antigravity agent |
| `modules/nf-core/emmtyper/main.nf` | nf-core-modules | `python -c import` eval, stub block, topic channels |
| `modules/nf-core/emmtyper/meta.yml` | nf-core-modules | Auto-generated + EDAM comment restored |
| `modules/nf-core/emmtyper/tests/main.nf.test` | nf-core-modules | `sanitizeOutput()` wrapper on all snapshots |

---

## Phase 5: Cross-Repo Sync

### Push Summary

| Repo | Branch | Remote | Status |
|---|---|---|---|
| `ngs-variant-validator` | `ngs_nf_hack` | `origin` (HReed1) | ✅ Pushed (6 commits) |
| `nf-core-modules` | `stub-topics-emmtyper` | `origin` (HReed1/modules) | ✅ Pushed (6 commits) → PR #11377 |
| `seqeralabs-docs` | `feat/skill-antigravity-gemini` | `fork` (HReed1/docs) | ✅ Pushed (2 commits) |
| `hvr-agentic-os` | `main` | `origin` (HReed1) | ✅ Pushed (1 sync commit, 847 insertions) |

---

## Key Technical Decisions

### 1. Shell-based Seqera AI Integration (not MCP)
Seqera AI was integrated via `run_command` shell invocation rather than as an MCP server. This was deliberate:
- Seqera AI manages its own authentication (`seqera login`)
- No custom tools needed — the CLI is self-contained
- Avoids MCP socket overhead for what is essentially a query/response pattern
- Portable across any agent platform that can execute shell commands

### 2. Python Import for Version Extraction
For Python/Click-based bioinformatics tools, `python -c "import pkg; print(pkg.__version__)"` is strictly preferred over `tool --version | sed` because:
- Click CLI output format varies between Click 7 and Click 8
- Python import works identically in Docker and Conda
- No fragile sed regex patterns to maintain

### 3. EDAM Comment Restoration as Script (not upstream fix)
Rather than contributing a fix to `nf-core/tools` to switch from PyYAML to ruamel.yaml round-trip mode (which would preserve comments), we opted for a lightweight local script. This is pragmatic for the short term while a proper upstream fix is a potential future contribution.

---

## Next Steps

1. **Batch Migration**: Begin systematic migration of remaining ~39 modules using the [validated template](../nextflow/walkthroughs/2026-04-29_emmtyper_pilot_retrospective.md#module-migration-template-for-the-next-39)
2. **Legacy PR Cleanup**: Close superseded PRs #11349–#11358 and replace with atomic 1-module PRs
3. **Upstream nf-core/tools Fix**: Consider contributing ruamel.yaml round-trip mode to preserve EDAM comments natively
4. **Seqera Docs PR**: Open PR against `seqeralabs/docs` for the Antigravity skill page (currently on fork branch)

**Status: SESSION COMPLETE — ALL REPOS IN SYNC**
