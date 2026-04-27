# Nextflow 2026 Hackathon — Ingestion & Triage Walkthrough

## Phase 1: Ingestion Complete ✅

Successfully ingested all **739 items** from [nf-core Project #146 — Hackathon March 2026](https://github.com/orgs/nf-core/projects/146) using `gh api graphql` with paginated cursor-based queries (8 pages, 100 items/page).

### Board Snapshot

| Metric | Value |
|---|---|
| **Total Items** | 739 |
| **Issues** | 649 |
| **Pull Requests** | 90 |
| **Open & Unassigned (To-do)** | 72 |

### By Status Column

| Status | Count |
|---|---|
| Done | 316 |
| No status set | 179 |
| In progress | 124 |
| To do | 82 |
| Ready for review | 38 |

### By Project Group

| Group | Count |
|---|---|
| Modules & Subworkflows | 311 |
| Pipelines | 186 |
| Documentation | 88 |
| Unset | 137 |
| Infrastructure | 11 |
| Nextflow & Plugins | 6 |

### Top Repositories

| Repository | Items |
|---|---|
| `nf-core/modules` | 363 |
| `nf-core/website` | 98 |
| `nf-core/proteinfold` | 45 |
| `nf-core/bacass` | 19 |
| `nf-core/seqinspector` | 18 |
| `nf-core/viralrecon` | 17 |
| `nf-core/genomeqc` | 16 |
| `nf-core/tools` | 15 |
| `nf-core/seqsubmit` | 15 |

### Data Saved To

- [hackathon_issues.json](file:///Users/harrisonreed/Projects/ngs-variant-validator/scripts/hackathon/hackathon_issues.json) — 739 items with full metadata
- [ingest_hackathon_issues.py](file:///Users/harrisonreed/Projects/ngs-variant-validator/scripts/hackathon/ingest_hackathon_issues.py) — Rerunnable ingestion script

---

## Phase 2: Triage Results

Scored 71 open/unassigned issues using the weighted matrix (35% Swarm Capability, 25% Label Priority, 20% Complexity, 10% Freshness, 10% Assignee Availability).

### Top 5 Candidates

---

#### 🥇 1. `nf-core/modules#5409` — Module stub that `touch .gz` break snapshots in nf-test
**Score: 7.5** | [View Issue](https://github.com/nf-core/modules/issues/5409)

| Dimension | Score |
|---|---|
| Swarm Capability | 8 |
| Label Priority | 7 (`bug` + `good first issue`) |
| Complexity | 5 |

**What it is:** Modules use `touch filename.gz` in their stub blocks, creating empty files that aren't valid gzip. This breaks `nf-test` snapshot assertions with `EOFException`. The fix is to replace `touch file.gz` with `echo '' | gzip > file.gz`.

**Why the swarm excels here:**
- Pure regex/grep + sed pattern: find `touch *.gz` → replace with `echo '' | gzip > *.gz`
- **19 modules** still need fixing (latest comment from March 2026)
- Each module is an independent, isolated file change
- No biological domain knowledge required
- Well-documented fix pattern with merged PRs as examples

**Risk:** Some modules conditionally touch `.gz` (e.g., when `compress` flag is true) — needs AST-level care, not blind sed.

> [!TIP]
> **This is the strongest first target.** It's a systematic, well-scoped bug fix across multiple independent modules. The swarm can process each of the 19 remaining modules as an isolated unit, and the fix pattern is deterministic.

---

#### 🥈 2. `nf-core/modules#10775` — Migration to topics channels: `drep/compare`
**Score: 7.5** | [View Issue](https://github.com/nf-core/modules/issues/10775)

| Dimension | Score |
|---|---|
| Swarm Capability | 7 |
| Label Priority | 5 (`good first issue`) |
| Complexity | 9 |

**What it is:** Part of a massive coordinated migration to Nextflow topic channels. Each sub-issue is a single module migration following a [documented guide](https://nf-co.re/docs/tutorials/migrate_to_topics/update_modules).

**Why the swarm excels here:**
- Single module, well-documented procedure
- Clear workflow: update output channels → fix `meta.yml` → update test snapshots
- Hundreds of identical PRs already merged — rich training data

**Risk:** Requires running `nf-core modules test` and `nf-core modules lint` locally, which needs Nextflow + nf-core tools installed.

---

#### 🥉 3. `nf-core/modules#3654` — Multiple samtools modules use `task.cpus-1` without checking lower boundary
**Score: 6.7** | [View Issue](https://github.com/nf-core/modules/issues/3654)

| Dimension | Score |
|---|---|
| Swarm Capability | 8 |
| Label Priority | 2 (`bug`) |
| Complexity | 7 |

**What it is:** Several samtools modules (depth, index, merge) set `--threads ${task.cpus - 1}` which produces `-1` or `0` when `task.cpus = 1`. The fix is to add a `Math.max()` guard.

**Why the swarm excels here:**
- Pure Groovy/Nextflow DSL2 fix — `Math.max(task.cpus - 1, 1)`
- Systematic: grep for the pattern across all samtools modules
- No bio knowledge needed

**Risk:** Recent comment (March 2026) questions whether `--threads 0` is actually invalid for samtools index. Needs clarification before fixing.

---

#### 4. `nf-core/tools#4088` — Configbuilder: refactor & clean up code
**Score: 6.8** | [View Issue](https://github.com/nf-core/tools/issues/4088)

| Dimension | Score |
|---|---|
| Swarm Capability | 10 |
| Label Priority | 1 (`enhancement`) |
| Complexity | 5 |

**What it is:** Python refactor of the nf-core configbuilder TUI (Textual-based). Standardize button press handling, clean up screen loading.

**Why the swarm excels here:**
- Pure Python — the swarm's strongest capability
- `nf-core/tools` has a full `pytest` suite
- Refactoring/cleanup is a well-defined mechanical task

**Risk:** Larger scope — touching UI/TUI code requires understanding Textual framework patterns. Multiple files involved.

---

#### 5. `nf-core/genomeqc#180` — Ensure all modules use version topic channels
**Score: 7.8** | [View Issue](https://github.com/nf-core/genomeqc/issues/180)

| Dimension | Score |
|---|---|
| Swarm Capability | 7 |
| Label Priority | 6 (`enhancement` + `good first issue`) |
| Complexity | 9 |

**What it is:** Ensure the genomeqc pipeline's modules all use version topic channels, and update the workflow scope to parse versions correctly.

**Why the swarm excels here:**
- Small, well-scoped pipeline
- Similar pattern to the modules topic channel migration
- Single pipeline repo

**Risk:** Very sparse issue body — might need to read the codebase to fully understand scope.

---

## Recommendation

> [!IMPORTANT]
> **Recommended First Target: `nf-core/modules#5409`** — Fix stub `touch .gz` patterns
>
> **Rationale:**
> 1. **19 independent, identical fixes** — each is a separate module file, isolatable
> 2. **Deterministic fix pattern** — `touch file.gz` → `echo '' | gzip > file.gz`
> 3. **Tagged `bug` + `good first issue`** — high hackathon signal
> 4. **Already partially completed** — extensive checklist shows what's done vs. remaining
> 5. **No bio domain knowledge** — pure shell/Nextflow DSL2 scripting
> 6. **Excellent PR template** — dozens of merged PRs to model after
>
> We can batch-submit fixes for all 19 remaining modules in a single PR (as the last commenter attempted) or as individual PRs per module.

---

## Next Steps

Awaiting your decision:
1. **Confirm target issue** — Do you want to proceed with `modules#5409` or pick a different candidate?
2. **PR strategy** — Single batch PR for all 19 modules, or individual PRs per module?
3. **Local tooling** — Do you have `nf-core tools` and Nextflow installed for running module tests, or should the swarm skip local testing and rely on CI?
