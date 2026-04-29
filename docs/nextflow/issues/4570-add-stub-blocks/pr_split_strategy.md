# PR #11323 Split Strategy — Issue #4570

> **Parent PR:** [nf-core/modules#11323](https://github.com/nf-core/modules/pull/11323) — Original monolithic stub PR
> **Parent Issue:** [nf-core/modules#4570](https://github.com/nf-core/modules/issues/4570) — `[FEATURE] Add stub support to every module`
> **Prior Art:** [PR #11312](https://github.com/nf-core/modules/pull/11312) (Issue #5409 — stub `.gz` fix, merged)

---

## Background

PR #11323 was submitted as a single monolithic PR covering 40+ modules. A reviewer
[requested](https://github.com/nf-core/modules/pull/11323#issuecomment-4334025913)
that we split it into smaller, focused PRs grouped by functional category.

This document specifies the 10-branch split strategy and tracks submission status.

> [!WARNING]
> **Status Update (2026-04-29):** PRs #11349–#11358 are **superseded** by the new atomic "1-module-per-PR" strategy. Each module will be submitted as its own PR, combining stub + topic channel migration. The pilot PR for this new strategy is [#11377 (emmtyper)](https://github.com/nf-core/modules/pull/11377) — now ✅ CI green.

---

## Branch Architecture

All branches are based on `upstream/master` with a single atomic commit each.
Each branch includes:
- `main.nf` stub blocks
- `tests/main.nf.test` stub test cases
- `tests/main.nf.test.snap` generated snapshots

### Phase 1 Branches (from original #11323 work)

| # | PR | Branch | Modules | Count |
|---|---|---|---|---|
| 1 | [#11349](https://github.com/nf-core/modules/pull/11349) | `stub/assemblers` | medaka, racon, raven, salsa2, shasta, shovill | 6 |
| 2 | [#11350](https://github.com/nf-core/modules/pull/11350) | `stub/qc-filtering` | fastqscan, filtlong, prinseqplusplus, pycoqc, rasusa | 5 |
| 3 | [#11351](https://github.com/nf-core/modules/pull/11351) | `stub/typing-annotation` | ectyper, emmtyper, kofamscan, mlst, scoary, seqsero2 | 6 |
| 4 | [#11352](https://github.com/nf-core/modules/pull/11352) | `stub/phylogenetics` | fasttree, rapidnj | 2 |
| 5 | [#11353](https://github.com/nf-core/modules/pull/11353) | `stub/utilities` | ffq, mygene, ncbigenomedownload, maltextract, islandpath, shasum, plasmidid | 7 |

### Phase 2 Branches (remaining 14 modules)

| # | PR | Branch | Modules | Count |
|---|---|---|---|---|
| 6 | [#11354](https://github.com/nf-core/modules/pull/11354) | `stub/variant-calling` | genrich, whamg | 2 |
| 7 | [#11355](https://github.com/nf-core/modules/pull/11355) | `stub/typing-annotation-2` | optitype, sistr, ssuissero, staphopiasccmec | 4 |
| 8 | [#11356](https://github.com/nf-core/modules/pull/11356) | `stub/qc-filtering-2` | sickle, slimfastq | 2 |
| 9 | [#11357](https://github.com/nf-core/modules/pull/11357) | `stub/pangenomics` | smoothxg, wfmash | 2 |
| 10 | [#11358](https://github.com/nf-core/modules/pull/11358) | `stub/misc-utilities` | pairix, tailfindr, snpdists, zip | 4 |

**Total: 40 modules across 10 PRs**

> [!NOTE]
> Of the 44 modules in the [original #4570 checklist](https://github.com/nf-core/modules/issues/4570#issuecomment-3998972222), 4 were excluded because stubs were already merged upstream by other contributors:
> `bioawk`, `clonalframeml`, `deepvariant`, `plasmidfinder`.

---

## Module Classification

### By Output Complexity

| Tier | Pattern | Modules |
|---|---|---|
| 🟢 Simple `touch` | Plain-text outputs (`.tsv`, `.txt`, `.bed`, `.fasta`) | mlst, shasum, snpdists, ffq, mygene, sistr, ectyper, emmtyper, rapidnj, fasttree, scoary, ssuissero, staphopiasccmec |
| 🟡 Compressed | At least one `.gz` output requiring `echo | gzip >` | medaka, filtlong, racon, rasusa, fastqscan, prinseqplusplus, sickle, slimfastq, pycoqc, tailfindr, shasta, raven |
| 🟠 Multi-output | Multiple output channels, some `optional: true` | shovill, genrich, smoothxg, wfmash, whamg, plasmidid, optitype, maltextract, salsa2 |
| 🔴 Edge cases | Archive formats, directory outputs, unusual patterns | zip, islandpath, kofamscan, ncbigenomedownload, pairix, seqsero2 |

### By Version Pattern

| Pattern | Modules | Stub Behavior |
|---|---|---|
| `path "versions.yml"` | ~36 modules | Stub must emit `versions.yml` via `cat <<-END_VERSIONS` |
| `topic: versions` | shovill, filtlong, zip, shasum | No `versions.yml` needed — topic channel handles it |

---

## Stub Block Design Patterns

### Pattern A: Simple Touch
```groovy
stub:
def prefix = task.ext.prefix ?: "${meta.id}"
"""
touch ${prefix}.tsv

cat <<-END_VERSIONS > versions.yml
"${task.process}":
    toolname: \$(echo \$(toolname --version 2>&1) | sed 's/....//')
END_VERSIONS
"""
```

### Pattern B: Compressed Output
```groovy
stub:
def prefix = task.ext.prefix ?: "${meta.id}"
"""
echo | gzip > ${prefix}.fastq.gz

cat <<-END_VERSIONS > versions.yml
"${task.process}":
    toolname: \$(echo \$(toolname --version 2>&1) | sed 's/....//')
END_VERSIONS
"""
```

### Pattern C: Multi-Output with Optionals
```groovy
stub:
def prefix = task.ext.prefix ?: "${meta.id}"
"""
touch ${prefix}.narrowPeak
touch ${prefix}.pileup.bedGraph
touch ${prefix}.pvalues.bedGraph
touch ${prefix}.intervals.bed
touch ${prefix}.duplicates.txt

cat <<-END_VERSIONS > versions.yml
"${task.process}":
    toolname: \$(echo \$(toolname --version 2>&1) | sed 's/....//')
END_VERSIONS
"""
```

### Pattern D: Topic-Channel Version (no versions.yml)
```groovy
stub:
def prefix = task.ext.prefix ?: "${meta.id}"
"""
touch ${prefix}.zip
"""
```

---

## Stub Test Design Pattern

All stub tests follow this nf-core standard structure:

```groovy
test("modulename - stub") {

    options "-stub"

    when {
        process {
            """
            input[0] = [
                [ id:'test', single_end:false ],
                [ file(params.modules_testdata_base_path + 'path/to/test.file', checkIfExists: true) ],
            ]
            """
        }
    }

    then {
        assertAll(
            { assert process.success },
            { assert snapshot(sanitizeOutput(process.out)).match() }
        )
    }
}
```

> [!IMPORTANT]
> Snapshot files (`main.nf.test.snap`) MUST be committed with the PR.
> They are auto-generated by `nf-test --update-snapshot` and verified by reviewers.

> [!CAUTION]
> Always use `sanitizeOutput(process.out)` from [nft-utils](https://github.com/nf-core/nft-utils), **not** raw `snapshot(process.out)`. This normalizes volatile version tuples from topic channels. Reviewers will reject PRs without it.

---

## Validation Status

All 14 Phase 2 stub tests have been locally validated:

| Module | Branch | nf-test Stub | Snapshot |
|---|---|---|---|
| genrich | `stub/variant-calling` | ✅ PASSED | ✅ Created |
| whamg | `stub/variant-calling` | ✅ PASSED | ✅ Created |
| optitype | `stub/typing-annotation-2` | ✅ PASSED | ✅ Created |
| sistr | `stub/typing-annotation-2` | ✅ PASSED | ✅ Created |
| ssuissero | `stub/typing-annotation-2` | ✅ PASSED | ✅ Created |
| staphopiasccmec | `stub/typing-annotation-2` | ✅ PASSED | ✅ Created |
| sickle | `stub/qc-filtering-2` | ✅ PASSED | ✅ Created |
| slimfastq | `stub/qc-filtering-2` | ✅ PASSED | ✅ Created |
| smoothxg | `stub/pangenomics` | ✅ PASSED | ✅ Created |
| wfmash | `stub/pangenomics` | ✅ PASSED | ✅ Created |
| pairix | `stub/misc-utilities` | ✅ PASSED | ✅ Created |
| tailfindr | `stub/misc-utilities` | ✅ PASSED | ✅ Created |
| snpdists | `stub/misc-utilities` | ✅ PASSED | ✅ Created |
| zip | `stub/misc-utilities` | ✅ PASSED | ✅ Created |

---

## Diff Artifacts

All diffs are archived at:
```
docs/nextflow/hackathon/diffs_issue_11323/
├── assemblers.diff
├── qc-filtering.diff
├── typing-annotation.diff
├── phylogenetics.diff
├── utilities.diff
├── variant-calling.diff
├── typing-annotation-2.diff
├── qc-filtering-2.diff
├── pangenomics.diff
└── misc-utilities.diff
```

---

## Submission Protocol

> [!CAUTION]
> Per GEMINI.md guardrails, each of the following actions requires **explicit per-action human approval**.
> Approval of this strategy document does NOT constitute approval for remote operations.

### Per-Branch Submission Sequence

1. `git push origin <branch>` — **GATE: Human approves push**
2. Create PR to `nf-core/modules` targeting `master` — **GATE: Human approves PR**
3. Add label "Ready for Review"
4. If CI reports formatting issues → comment `@nf-core-bot fix linting`

### PR Description Template

```markdown
## Description

Adds deterministic `stub:` blocks and corresponding `-stub` nf-test cases for
[CATEGORY] modules, as part of the ongoing effort to resolve #4570.

Split from the original monolithic #11323 per reviewer feedback.

## Modules

- module1 (brief description)
- module2 (brief description)

## Tests

All modules include `-stub` test cases with `assertAll()` + `snapshot(process.out).match()`.
Snapshots generated locally via `nf-test --update-snapshot`.

## Checklist

- [x] Stub blocks produce valid placeholder files for all output channels
- [x] Compressed outputs use `echo | gzip >` (not `touch`)
- [x] `versions.yml` emission matches script block (where applicable)
- [x] nf-test stub tests pass locally
- [x] Snapshots committed
```

### Post-Submission

- Comment on PR #11323 linking all split PRs
- Leave #11323 open with a reference comment (do not close until splits are merged)

---

## Anti-Patterns (Lessons from #5409 and #11323)

1. ❌ **Quoted echo in gzip:** `echo "" | gzip >` or `echo '' | gzip >` produces different byte output than bare `echo | gzip >`. Always use `echo | gzip >` (no quotes, no arguments). See [PR #11312 reviewer feedback](https://github.com/nf-core/modules/pull/11312#discussion_r3146198459).
2. ❌ **Scope creep:** Do NOT fix module bugs, update containers, or refactor while adding stubs.
3. ❌ **Monolithic PRs:** Reviewers explicitly requested focused, category-based splits. Now superseded by 1-module-per-PR.
4. ❌ **Missing snapshots:** Snapshot files MUST be committed. Tests fail without them.
5. ❌ **Config conflicts:** Stub tests must not rely on `params.module_args` unless defined in the `when` block.
6. ❌ **Skipping human gates:** Every external GitHub operation needs explicit per-action approval.
7. ❌ **Hand-editing `meta.yml`:** It is auto-generated by `nf-core modules lint --fix`. Manual edits drift from `main.nf` and cause both lint and prettier CI failures.
8. ❌ **Using `echo $()` in eval():** Python tracebacks containing parentheses crash bash. Always pipe directly.
9. ❌ **Skipping `sanitizeOutput()`:** Topic channels add volatile version tuples. Raw `snapshot(process.out)` creates brittle snapshots rejected by reviewers.
10. ❌ **Skipping `prettier --check`:** The pre-commit CI normalizes YAML quoting. Hand-written YAML strings often use different quoting than prettier expects.
11. ❌ **Using `--version | sed` for Python/Click tools:** Click's output format differs across versions. Use `python -c "import pkg; print(pkg.__version__)"` instead.

---

## Related Documents

| Document | Description |
|---|---|
| [📋 Implementation Plan](implementation_plan.md) | Research and implementation strategy for adding stubs to 44 modules |
| [✅ Validation Report](validation_report.md) | Full test results for all 40 modules (Phase 1 + Phase 2) |
| [🏗️ Swarm Architecture](swarm_architecture.md) | Technical case study of the agentic swarm execution |
| [📂 Issue #5409 Plan](../5409-fix-stub-gz/implementation_plan.md) | Prior art — the stub `.gz` fix that preceded this work |
| [📂 Archived Diffs](../../hackathon/diffs_issue_11323/) | 10 category-based diff files for each split PR branch |
| [📖 nf-core Contributing Reference](../../reference/nfcore_contributing_reference.md) | Internalized nf-core conventions and workflow |
| [🔙 Nextflow Docs Index](../../README.md) | Main documentation index |
