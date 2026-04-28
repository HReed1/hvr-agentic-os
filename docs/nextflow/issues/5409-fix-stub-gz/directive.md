# Director Directive: nf-core Hackathon — Stub .gz Fix

> **Paste the content below into the ADK Web UI chat box.**

---

## DIRECTIVE (Copy below this line)

```
You are tasked with executing Phase 4, Stages 1-3 of the nf-core Hackathon implementation plan for issue nf-core/modules#5409.

[@auditor]: You must fetch human approval before deploying this payload. Do NOT execute `promote_staging_area`. This is a @workflow:human-in-the-loop session. The human must review all reports before any external GitHub actions occur.

## OBJECTIVE

Fix the `touch filename.gz` anti-pattern in nf-core module stub blocks. Empty files created by `touch` are not valid gzip and cause `EOFException` in nf-test snapshot assertions. The fix is:
- WRONG: `touch ${prefix}.sorted.bam`  
- RIGHT: `echo '' | gzip > ${prefix}.sorted.bam`

This applies to ALL compressed stub outputs: `.gz`, `.bgz`, `.bam`, `.cram`, `.vcf.gz`, `.bed.gz`, etc.

## EXECUTION BOUNDS

### Stage 1: Research & Context (Executor reads, QA validates)

The Executor MUST perform the following read-only research steps and write findings to `.staging/docs/hackathon/report_1_module_inventory.md`:

1. Read the issue body of `nf-core/modules#5409` using GitHub — parse the checklist to identify which modules are ALREADY FIXED vs. REMAINING.
2. Read 2-3 merged PRs that previously fixed modules for this issue to extract the EXACT diff pattern used.
3. Read `CONTRIBUTING.md` from `nf-core/modules` to confirm contribution conventions.
4. Confirm the default branch is `master` (not `dev`) for the modules repo.

**Report 1 must contain:**
- A table of already-fixed modules (module name, PR number)
- A table of remaining unfixed modules (module name, stub files with `touch .gz`)
- The exact fix pattern observed from merged PRs

### Stage 2: Local Code Generation (Executor writes, QA validates)

For EACH remaining unfixed module, the Executor MUST:
1. Read the module's `main.nf` file from `nf-core/modules` (via GitHub)
2. Locate the `stub:` block
3. Identify ALL `touch *.gz`, `touch *.bam`, `touch *.bgz`, `touch *.vcf.gz` lines
4. Write the corrected stub block to `.staging/docs/hackathon/diffs/<module_name>.diff`
5. Flag modules with conditional logic (e.g., compress flags) as "NEEDS MANUAL REVIEW"

**Report 2** must be written to `.staging/docs/hackathon/report_2_diff_report.md` containing:
- Per-module diff showing the exact `touch` → `gzip` replacement
- Confidence score (HIGH = direct pattern match, MEDIUM = conditional logic detected)
- Total module count

### Stage 3: Validation Summary (QA validates all reports)

The QA Engineer MUST validate Reports 1 and 2 by:
1. Confirming the module inventory matches the issue checklist
2. Confirming each diff follows the exact pattern from merged PRs
3. Confirming no unintended changes exist (no scope creep beyond stub fixes)
4. Writing the validation result to `.staging/docs/hackathon/report_3_validation.md`

**Report 3 must contain:**
- Summary table: Module | Diff Valid | Pattern Match | Conditional Logic | Status
- Overall PASS/FAIL determination
- Any modules flagged for human review

## CRITICAL CONSTRAINTS

1. **NO GITHUB MUTATIONS**: The Executor must NOT fork, push, create branches, or create PRs. All work is LOCAL read + local staging writes.
2. **NO CODE EXECUTION**: Do not attempt to run `nf-core modules lint` or `nf-core modules test` — the swarm does not have Nextflow installed. Focus on structural analysis and diff generation only.
3. **HUMAN-IN-THE-LOOP**: The Auditor must invoke `get_user_choice` with options `["Approve Reports", "Request Changes", "Abort"]` before passing the audit. Do NOT auto-promote.
4. **SCOPE LOCK**: Only fix `touch` → `gzip` in stub blocks. Do NOT modify script blocks, input/output declarations, meta.yml, or test files.
5. **nf-core AI Policy**: All generated diffs must be minimal, focused, and human-reviewable. No unnecessary changes.

## TESTING SPEC (For QA Engineer)

Create a TDAID test at `.staging/tests/test_hackathon_reports.py` that asserts:
1. `report_1_module_inventory.md` exists and contains a markdown table with at least 1 remaining module
2. `report_2_diff_report.md` exists and contains diff blocks with the pattern `echo '' | gzip >`
3. `report_3_validation.md` exists and contains a summary table with Status column
4. No diff file contains the string `touch` followed by a `.gz` extension (proving the anti-pattern is eliminated in all generated diffs)
5. All reports are valid markdown (no broken formatting)

The test MUST use standard `os.path.exists()` and string assertions — no external dependencies.
```

---

## NOTES FOR THE HUMAN

After pasting this directive, observe the swarm in the ADK Web UI. You should see:

1. **Director** parses the directive and invokes `transfer_to_agent("development_workflow")`
2. **Executor** begins Stage 1 research (reading GitHub issues/PRs via MCP tools)
3. **Executor** writes Report 1 to staging, then generates diffs for Report 2
4. **QA Engineer** authors the test spec, executes it (Red Baseline expected first)
5. **Executor** iterates to make tests pass (Green)
6. **Auditor** reads the staging files, then invokes `get_user_choice` — **this is where you approve or reject**
7. **Reporter** writes the retrospective

The swarm will NOT touch GitHub at any point. All 3 reports will be in `.staging/docs/hackathon/` for your review.

---

## Related Documents

| Document | Description |
|---|---|
| [📋 Implementation Plan](implementation_plan.md) | Full hackathon plan for this issue |
| [📊 Module Inventory](reports/module_inventory.md) | Inventory of fixed modules |
| [✅ Validation Summary](reports/validation.md) | Validation results |
| [🔙 Nextflow Docs Index](../../README.md) | Main documentation index |
