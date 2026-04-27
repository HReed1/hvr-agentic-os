# nf-core/modules#4570 — Add Stub Blocks to Remaining 44 Modules

**Parent Issue:** [nf-core/modules#4570](https://github.com/nf-core/modules/issues/4570) — `[FEATURE] Add stub support to every module`
**Author:** @ewels (Phil Ewels)
**Project Board:** Hackathon March 2026
**Workflow:** `/nf-core-contribution`
**Prior Art:** [PR #11312](https://github.com/nf-core/modules/pull/11312) (Issue #5409 — stub `.gz` fix)

---

## Background

Issue #4570 mandates that every nf-core module has a `stub:` block. The community has driven this down from 1,095 modules to **44 remaining**. The latest comment on the issue provides the definitive checklist.

Our previous contribution (PR #11312 for Issue #5409) fixed *existing* stubs that produced invalid `.gz` files via `touch`. This new effort is **adding stubs where none exist at all** — a complementary but distinct scope.

> [!IMPORTANT]
> This is a **feature contribution**, not a bug fix. Each stub must correctly generate placeholder files matching the module's `output:` channel declarations.

---

## User Review Required

### Batching Strategy

> [!IMPORTANT]
> **44 modules in a single PR would be enormous.** Based on nf-core's AI/LLM policy ("keep PRs small and focused"), I recommend splitting into **4 batches of ~11 modules each**, grouped by output complexity. Each batch becomes one PR. However, the nf-core community may prefer larger batches since this is a known hackathon project.
>
> **Decision needed:** Do you want 4 focused PRs or 2 larger PRs?

### Deprecated Modules

> [!WARNING]
> **`deepvariant`** is already deprecated (the script block contains `assert false` with a deprecation message directing users to `deepvariant/rundeepvariant`). Adding a stub to a deprecated module is technically valid but questionable.
>
> **Decision needed:** Include `deepvariant` in the PR scope, or skip it and note in the PR description?

### `topic:` Version Channels

> [!IMPORTANT]
> Several modules (`shovill`, `filtlong`) use the newer `topic: versions` emit pattern instead of `path "versions.yml"`. Stub blocks for these modules do NOT need to emit `versions.yml` — the topic-based version is handled automatically by Nextflow. This changes the stub template for those modules.
>
> **Decision needed:** This is just an FYI — no action needed unless you disagree.

---

## Module Inventory & Complexity Analysis

### Sampled Modules (7/44 reviewed in detail)

| Module | Output Channels | Compressed? | Optional? | Version Pattern | Complexity |
|---|---|---|---|---|---|
| `deepvariant` | 4 (`.vcf.gz`, `.g.vcf.gz`, `.tbi`) | ✅ | ❌ | `versions.yml` | 🔴 Deprecated |
| `medaka` | 1 (`*.fa.gz`) | ✅ | ❌ | `versions.yml` | 🟡 |
| `mlst` | 1 (`*.tsv`) | ❌ | ❌ | `versions.yml` | 🟢 |
| `zip` | 1 (`*.zip`) | ❌ (archive) | ❌ | `versions.yml` | 🟡 |
| `shovill` | 4 (`.fa`, `.corrections`, `.log`, `.fasta`) + 1 optional | ❌ | ✅ | `topic:` | 🟠 |
| `filtlong` | 2 (`*.fastq.gz`, `*.log`) | ✅ | ❌ | `topic:` | 🟡 |
| `racon` | 1 (`*.fasta.gz`) | ✅ | ❌ | `versions.yml` | 🟡 |
| `smoothxg` | 2 (`*.gfa`, `*.maf` optional) | ❌ | ✅ | `versions.yml` | 🟠 |
| `genrich` | 1 (`*.narrowPeak`) + 4 optional | ❌ | ✅ | `versions.yml` | 🟠 |
| `shasum` | 1 (`*.sha256`) | ❌ | ❌ | `versions.yml` | 🟢 |

### Complexity Tiers (All 44 Modules)

#### 🟢 Tier 1 — Simple `touch` (est. ~15 modules)
Plain-text outputs only (`.tsv`, `.txt`, `.bed`, `.fasta`, `.log`). No compression, no optional channels.

**Candidate modules:** `bioawk`, `mlst`, `shasum`, `snpdists`, `ffq`, `mygene`, `sistr`, `ectyper`, `emmtyper`, `rapidnj`, `fasttree`, `clonalframeml`, `scoary`, `ssuissero`, `staphopiasccmec`

#### 🟡 Tier 2 — Compressed outputs (est. ~12 modules)
At least one `.gz` output requiring `echo "" | gzip >` pattern.

**Candidate modules:** `medaka`, `filtlong`, `racon`, `rasusa`, `fastqscan`, `prinseqplusplus`, `sickle`, `slimfastq`, `pycoqc`, `tailfindr`, `shasta`, `raven`

#### 🟠 Tier 3 — Multi-output / Optional channels (est. ~10 modules)
Multiple output channels, some `optional: true`, or glob patterns.

**Candidate modules:** `shovill`, `genrich`, `smoothxg`, `wfmash`, `whamg`, `plasmidfinder`, `plasmidid`, `optitype`, `maltextract`, `salsa2`

#### 🔴 Tier 4 — Edge cases (est. ~7 modules)
Deprecated modules, archive formats, or unusual patterns.

**Candidate modules:** `deepvariant`, `zip`, `islandpath`, `kofamscan`, `ncbigenomedownload`, `pairix`, `seqsero2`

> [!NOTE]
> These tier assignments are **estimates** based on sampling. The actual tier for each module will be confirmed during Phase 2 when we analyze all 44 `main.nf` files programmatically.

---

## Proposed Changes

### Phase 1: Programmatic Analysis (Local)

#### [NEW] `docs/nextflow/hackathon/scripts/stub_generator.py`

A Python script that:
1. Clones `nf-core/modules` to `/tmp/nf-core-modules-4570/`
2. Parses all 44 `main.nf` files to extract `output:` channel declarations
3. Classifies each module into a complexity tier
4. Generates the correct `stub:` block for each module based on output patterns
5. Produces a structured report: `report_4570_inventory.md`

**Stub generation rules:**

| Output Pattern | Stub Command |
|---|---|
| `path("*.ext")` or `path("${prefix}.ext")` | `touch ${prefix}.ext` |
| `path("*.gz")` or `path("${prefix}.fa.gz")` | `echo "" \| gzip > ${prefix}.fa.gz` |
| `path("*.vcf.gz.tbi")` | `touch ${prefix}.vcf.gz.tbi` |
| `path("*.zip")` | `touch ${prefix}.zip` |
| `path "versions.yml"` | Standard versions block (see template below) |
| `optional: true` channels | Include in stub with same `touch`/`gzip` pattern |
| `topic: versions` channels | **No versions.yml needed** — skip |

**Versions.yml stub template:**
```bash
cat <<-END_VERSIONS > versions.yml
"${task.process}":
    <tool>: \$(echo \$(<tool> --version 2>&1) | <sed pattern>)
END_VERSIONS
```

> [!IMPORTANT]
> The versions block in the stub MUST exactly match the versions block in the script. This is copy-pasted, not generated.

---

### Phase 2: Diff Generation & Validation

#### [NEW] `docs/nextflow/hackathon/diffs_issue_4570/`

Directory containing one `.diff` file per module. Each diff adds a `stub:` block immediately after the `script:` block (before the closing `}`).

**Stub block placement:**
```groovy
    script:
    // ... existing script block ...
    """

    stub:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    touch ${prefix}.tsv

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        mlst: \$( echo \$(mlst --version 2>&1) | sed 's/mlst //' )
    END_VERSIONS
    """
}
```

#### [NEW] `docs/nextflow/hackathon/report_4570_inventory.md`
Full inventory of all 44 modules with tier classification, output channels, and generated stub blocks.

#### [NEW] `docs/nextflow/hackathon/report_4570_validation.md`
Validation report confirming:
- All 44 modules now have `stub:` blocks
- All `.gz` outputs use `echo "" | gzip >` (double quotes)
- All non-`topic:` modules emit `versions.yml`
- Optional outputs are included

---

### Phase 3: Batched PR Submission (Gated)

Following `/nf-core-contribution` Phase 3 gate protocol:

| Batch | Modules | Tier | PR Branch |
|---|---|---|---|
| **Batch 1** | ~11 modules | 🟢 Simple | `add-stub-blocks-batch1` |
| **Batch 2** | ~11 modules | 🟡 Compressed | `add-stub-blocks-batch2` |
| **Batch 3** | ~11 modules | 🟠 Multi-output | `add-stub-blocks-batch3` |
| **Batch 4** | ~11 modules | 🔴 Edge cases | `add-stub-blocks-batch4` |

Each batch follows the full gate sequence:
1. **GATE 1:** Report review → Human approves analysis
2. **GATE 2:** Fork (already exists from #5409 work)
3. **GATE 3:** Push branch → Human approves push
4. **GATE 4:** Draft PR → Human approves PR creation
5. **GATE 5:** Lint remediation → CI stabilization
6. **GATE 6:** Ready for review → Human clicks "Ready"

---

## Verification Plan

### Automated Verification

1. **Grep verification:** After applying all diffs, run:
   ```bash
   for module in bioawk clonalframeml deepvariant ectyper emmtyper fastqscan fasttree ffq filtlong genrich islandpath kofamscan maltextract medaka mlst mygene ncbigenomedownload optitype pairix plasmidfinder plasmidid prinseqplusplus pycoqc racon rapidnj rasusa raven salsa2 scoary seqsero2 shasta shasum shovill sickle sistr slimfastq smoothxg snpdists ssuissero staphopiasccmec tailfindr wfmash whamg zip; do
     grep -l "stub:" /tmp/nf-core-modules-4570/modules/nf-core/${module}/main.nf || echo "MISSING: ${module}"
   done
   ```
   Expected: zero `MISSING` lines.

2. **Gzip convention check:**
   ```bash
   git diff --unified=0 | grep "^+" | grep -i "touch.*\.gz" && echo "FAIL: found touch .gz" || echo "PASS"
   ```
   Expected: `PASS` — no `.gz` files created with `touch`.

3. **TDAID validation:** Write pytest assertions validating the generated reports and diff structure.

### Manual Verification

- Lint each changed module locally: `nf-core modules lint <module-name>`
- Verify PR CI passes (nf-core's CI automatically lints all changed modules)
- Human reviews each batch before marking "Ready for Review"

---

## Known Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Some modules may have been fixed by other PRs since the list was posted | Cross-reference against live `master` before generating diffs |
| nf-core linter may enforce stub-run CI (`-stub-run`) | Start with Batch 1 (simplest modules) to validate the CI pattern |
| Deprecated modules may cause reviewer confusion | Document `deepvariant`'s deprecated status in PR description |
| Modules with `topic: versions` need different stub template | Script auto-detects version pattern and adapts |
| Pre-existing lint failures on changed modules | Document in PR comment table (per #5409 lesson) — do NOT fix |

---

## Anti-Patterns (from #5409 Hackathon)

These hard lessons are **mandatory** reading for the swarm:

1. ❌ **Single quotes in gzip:** `echo '' | gzip >` fails the linter. Use `echo "" | gzip >`.
2. ❌ **Scope creep:** Do NOT fix module bugs, update containers, or refactor while adding stubs.
3. ❌ **Fixing pre-existing lint failures:** Document them. Don't fix them.
4. ❌ **Stale checklists:** Verify against live `master` — some modules may already have stubs from other PRs.
5. ❌ **Cloning into workspace:** Use `/tmp/` for the fork clone.
6. ❌ **Skipping human gates:** Every external GitHub operation needs explicit per-action approval.
