# Diff Bucket Analysis: Issue #5409 Scope Split

## Summary

The swarm generated 101 diffs total. After cross-referencing against the issue's actual scope (`touch *.gz` only), they split cleanly into two non-overlapping buckets:

| Bucket | Count | Directory | PR Strategy |
|--------|-------|-----------|-------------|
| Issue #5409 (.gz) | 8 | `diffs_issue_5409_gz_only/` | Submit as PR against nf-core/modules for issue #5409 |
| Proactive (.bam/.cram/.bai/.bgz) | 94 | `diffs_proactive_bam_cram/` | Open new companion issue, then PR separately |

---

## Bucket 1: Issue-Scoped — `.gz` Only (8 modules)

These directly address the `touch *.gz` → `echo '' | gzip > *.gz` fix described in issue #5409.

| Module | Extensions Fixed | Note |
|--------|-----------------|------|
| bowtie2/align | `.fastq.gz` | Prior PR #7978 fixed `.bam`, but missed conditional `.fastq.gz` unmapped reads |
| gatk4/haplotypecaller | `.vcf.gz` | New fix |
| metamdbg/asm | `.fasta.gz` | New fix |
| pharokka/installdatabases | `.fas.gz` | New fix |
| popscle/freemuxlet | `.vcf.gz`, `.samples.gz` | New fix |
| rastair/methylkit | `.txt.gz` | New fix |
| staramr/search | `.tsv.gz`, `.txt.gz` | New fix |
| vt/decomposeblocksub | `.vcf.gz` | New fix (missed by swarm, added manually) |

> **8 genuinely new fixes** + 1 supplementary fix (bowtie2/align's remaining `.fastq.gz` stubs).

---

## Bucket 2: Proactive — `.bam`/`.cram`/`.bai` (93 modules)

These fix `touch *.bam` → `echo '' | gzip > *.bam`, which is **not in the issue scope** but is the same class of problem. BAM/CRAM are binary formats; a `touch`ed file has no magic bytes and will fail any format-aware reader.

### Why this is valid
- BAM files begin with `BAM\1` magic bytes — `touch` creates 0-byte files that crash `samtools` and BAM-aware nf-test assertions
- CRAM files require an EOF block — same failure mode
- `echo '' | gzip > file.bam` creates a valid gzip stream that won't crash snapshot comparisons

### Why it should be a separate issue/PR
- The maintainers scoped #5409 to `*.gz` explicitly via `git grep -cP "touch .*\.gz"`
- BAM/CRAM have different magic byte requirements — a more thorough fix might use `samtools view -H /dev/null -o stub.bam` instead of gzip
- Mixing scopes in one PR risks pushback and review delays

### Extensions breakdown
| Extension | Module Count |
|-----------|-------------|
| `.bam` | 86 |
| `.bam` + `.bam.bai` | 14 |
| `.bam` + `.cram` + `.cram.crai` | 1 (gatk4/markduplicates) |

---

## Recommended PR Strategy

1. **PR #1 (Issue #5409)**: Submit the 8 `.gz`-scoped diffs. Reference issue #5409, note that `bowtie2/align` is supplementary to PR #7978. Small, focused, easy to review.

2. **Issue #2 (New)**: Open a companion issue: *"Module stubs that `touch .bam/.cram` create invalid binary files"*. Reference #5409 as prior art. Include the analysis that BAM/CRAM stubs have the same structural failure mode.

3. **PR #2 (New Issue)**: Submit the 93 `.bam/.cram` diffs against the new issue. May want to batch into smaller PRs (e.g., by tool family: gatk4/*, samtools/*, picard/*, etc.).

---

## Related Documents

| Document | Description |
|---|---|
| [📋 Issue #5409 Plan](../issues/5409-fix-stub-gz/implementation_plan.md) | Hackathon plan for the stub `.gz` fix |
| [📊 Diff Report](../issues/5409-fix-stub-gz/reports/diff_report.md) | Per-module diff details |
| [📖 nf-core Contributing Reference](nfcore_contributing_reference.md) | Internalized nf-core conventions |
| [🔙 Nextflow Docs Index](../README.md) | Main documentation index |
