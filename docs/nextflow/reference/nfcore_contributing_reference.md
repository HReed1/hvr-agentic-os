# nf-core Contributing & Developing — Internalized Reference

> Distilled from the official nf-core documentation on 2026-04-26.
> Sources: `nf-core/website` — `/contributing/` and `/developing/` directories.

---

## 1. Contribution Workflow (Components — Our Target)

### 1.1 Pre-Flight Checks
1. **Check if component exists** — `nf-core modules list`, check repo + open PRs + open issues
2. **Create an issue** — title format: `"New module: {tool}"` or descriptive bug title. Self-assign.
3. **Fork → Clone → Branch**:
   ```bash
   git clone https://github.com/<username>/modules.git nf-core-modules
   cd nf-core-modules
   git remote add upstream https://github.com/nf-core/modules.git
   git checkout -b <component-name>
   ```
4. **Install pre-commit hooks**: `pre-commit install`

### 1.2 Branch Naming
- For modules: name branch after component (e.g., `samtools/depth-fix`)
- For pipelines: descriptive names like `add-fastqc-module` or `fix-memory-issue`

### 1.3 Commit & Push
```bash
git add .
git commit -m "Add new component: <component-name>"
git pull --rebase upstream master   # ← IMPORTANT: rebase against master for modules
git push origin <component-name>
```

> [!IMPORTANT]
> **For `nf-core/modules`**: rebase against `upstream master` (not `dev`).
> **For pipelines**: rebase against `upstream dev` and PR into `dev` (never `master`).

### 1.4 PR Creation
- Use the repository's PR template
- Reference the related issue
- Describe changes, testing, and include example commands/screenshots
- Add **"Ready for Review"** label
- Request reviews from `nf-core/modules-team`
- Can use `@nf-core-bot fix linting` to auto-fix formatting issues

---

## 2. AI/LLM Usage Policy

> **nf-core stance**: Humans are ultimately responsible for submitted code, regardless of tools used.

Guidelines for AI-assisted contributions:
1. Keep PRs as **small and focused as possible**
2. **Avoid unnecessary changes** — no moving or refactoring code unless that's the PR's intent
3. **Review all generated code yourself** before opening a PR — ensure you understand it
4. **Engage with the community review process** and expect to make revisions

---

## 3. Component Structure (Modules)

A module consists of these files:

| File | Purpose |
|---|---|
| `environment.yml` | Conda environment (used by env + container engines) |
| `main.nf` | Process definition with tool command |
| `meta.yml` | Metadata: author, inputs, outputs, descriptions. Validated against JSON schema |
| `tests/main.nf.test` | nf-test test workflow |
| `tests/main.nf.test.snap` | Snapshot reference file (auto-generated) |
| `tests/nextflow.config` | Optional test-specific config |

### 3.1 Key `main.nf` Conventions
- **Meta maps**: Only `meta.id` and `meta.single_end` are allowed in modules. All other meta usage via `ext.args`
- **File prefix**: `def prefix = task.ext.prefix ?: "${meta.id}"`
- **Args**: `def args = task.ext.args ?: ''`
- **Tag**: `tag "${meta.id}"`
- **Optional params**: Must go through `$args` (i.e., `ext.args`), NOT hardcoded
- **Version output**: Must use eval output qualifiers for version channels
- **Stubs**: Must produce valid files (our target issue — `touch file.gz` is WRONG, need `echo '' | gzip > file.gz`)

### 3.2 ext.args System
- `ext.args` — primary command-line args injection
- `ext.args2`, `ext.args3` — for multi-tool modules
- `ext.prefix` — file name prefix override
- `ext.when` — conditional execution
- Numeric order MUST match tool order in script

### 3.3 Meta Maps
- Only 2 standard keys: `meta.id` and `meta.single_end`
- Modules MUST NOT reference any other meta keys directly
- Other meta data flows through `ext.args` in `modules.config`

---

## 4. Testing Framework (nf-test)

### 4.1 Core Guidelines for Assertions
1. **Encapsulate in `assertAll()`** — group all assertions
2. **Minimum requirements**: check `process.success` + snapshot `versions`
3. **Capture as much as possible** — prefer full output snapshots
4. **Handle inconsistent MD5s** — use content checks for unstable outputs
5. **Verify module functionality** — snapshots must reflect actual module behavior

### 4.2 Assertion Patterns

**Simple — snapshot entire output:**
```groovy
assertAll(
    { assert process.success },
    { assert snapshot(process.out).match() }
)
```

**Minimum — success + versions:**
```groovy
assertAll(
    { assert process.success },
    { assert snapshot(process.out.versions).match("versions") }
)
```

**File exists check (for unstable outputs):**
```groovy
assert file(process.out.interop[0][1].find { file(it).name == "IndexMetricsOut.bin" }).exists()
```

**File content checks:**
```groovy
assert path(get(1)).readLines().last().contains("Expected string")
```

### 4.3 Snapshot Mechanics
- First run generates `.nf.test.snap` JSON file
- Subsequent runs compare against it
- **MUST commit snapshot files** with code changes
- Reviewers check snapshots during review
- MD5 fingerprints replace paths for consistency
- Use `[0..4]` slicing for partial file snapshots
- `.linesGzip` for gzipped file content

### 4.4 Testing Commands
```bash
# Lint
nf-core modules lint <module-name>

# Test
nf-core modules test <module-name>
```

---

## 5. Component Review Checklist (What Reviewers Check)

### General
- [ ] Adheres to module/subworkflow specifications
- [ ] All CI checks pass (linting, conda, singularity, docker)
- [ ] Runs offline — no automatic DB downloads
- [ ] Code uses meta map correctly
- [ ] Code is readable, properly formatted

### main.nf
- [ ] Optional params in `$args` section
- [ ] Software version extraction is optimized
- [ ] Bioconda version is latest
- [ ] Temp unzipped files are cleaned up
- [ ] Large outputs use correct compression

### Tests & Metadata
- [ ] Tests exist for ALL outputs (including optional)
- [ ] `meta.yml` has correct doc links and file patterns
- [ ] `meta.yml` has correct `bio.tools` ID and EDAM ontology links
- [ ] Tool help checked for missed important inputs
- [ ] nf-test runs successfully and captures all outputs

---

## 6. nf-core Bot Commands

| Command | Action |
|---|---|
| `@nf-core-bot fix linting` | Auto-fix prettier formatting issues |
| `@nf-core-bot update gpu snapshot path: $PATH` | Update GPU-based nf-test snapshots |
| `@nf-core-bot update changelog` | Update auto-generated changelog |
| `@nf-core-bot update snapshots` | Update Textual snapshot tests |

---

## 7. Pipeline Contribution Conventions (for pipeline-level PRs)

### Channel Naming
- Initial output: `ch_output_from_<process>`
- Intermediate: `ch_<previousprocess>_for_<nextprocess>`

### Resource Requirements
- Defined in `conf/base.config` using `withLabel:` selectors
- Use standardized labels: `process_low`, `process_medium`, `process_high`
- Reference dynamically: `${task.cpus}`, `${task.memory}`

### Parameters
- Define defaults in `nextflow.config` under `params` scope
- Update schema: `nf-core pipelines schema build`

### Testing
```bash
nextflow run . -profile debug,test,docker --outdir <outdir>
nf-core pipelines lint .
```

### PR Target
- **Always PR into `dev`** (never `master`)
- Exception: critical hotfix patches go to `master` with version bump

---

## 8. Critical Corrections to Our Implementation Plan

Based on this documentation review, the following items in our current implementation plan need updating:

### ❌ Old Plan Errors → ✅ Corrections

1. **PR target branch for modules**:
   - ❌ Plan says: "Target branch: `dev`"
   - ✅ Correct: For `nf-core/modules`, PRs target `master` branch. Rebase against `upstream master`.
   - (Only pipelines use `dev`)

2. **Commit message format**:
   - ❌ Plan says: `fix(modules): {description} (closes #{issue})`
   - ✅ Correct: Use nf-core's format: `"Add new component: <name>"` or descriptive message. The conventional commit format is not mandated by nf-core.

3. **Branch naming**:
   - ❌ Plan says: `hackathon/fix-{issue-number}-{slug}`
   - ✅ Correct: Name branch after the component/fix — e.g., `fix-stub-gzip` or `samtools/depth-thread-guard`

4. **Testing commands**:
   - ❌ Plan says: `nf-test test modules/nf-core/{module}/tests/`
   - ✅ Correct: Use `nf-core modules test <module-name>` and `nf-core modules lint <module-name>`

5. **Pre-commit hooks**:
   - ❌ Plan doesn't mention pre-commit
   - ✅ Must run `pre-commit install` after cloning fork

6. **Draft PRs**:
   - ❌ Plan says: start as draft
   - ✅ Correct: Add "Ready for Review" label when ready. Use `@nf-core-bot fix linting` for formatting.

7. **Review process**:
   - ❌ Plan doesn't account for nf-core review etiquette
   - ✅ Must: Request review from `nf-core/modules-team`, use `#request-review` Slack channel, prefer `Comments` review type over `Request changes`

8. **AI disclosure**:
   - ❌ Plan doesn't mention AI policy
   - ✅ Must: Keep PRs small/focused, review all generated code, engage with review process. Humans responsible for submitted code.

9. **Snapshot updates**:
   - ❌ Plan doesn't cover snapshot management
   - ✅ Must: Update `.nf.test.snap` files when fixing stubs, commit snapshots with changes, ensure `assertAll()` pattern used
