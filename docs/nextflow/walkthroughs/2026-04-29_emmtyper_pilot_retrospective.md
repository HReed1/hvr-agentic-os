# Emmtyper Pilot PR Retrospective — Lessons for the Next 39 Modules

## PR: [nf-core/modules#11377](https://github.com/nf-core/modules/pull/11377) — ✅ Green

---

## Timeline: 5 Pushes to Green

| Push | Commit | Issue | Fix |
|---|---|---|---|
| 1 | `1eb9d9c` | Initial submission | Topic migration + stub + tests |
| 2 | `8a9d392` | Snapshot didn't match | Regenerated with `--update` |
| 3 | `05ac16e` | `eval()` Conda bash crash + missing `sanitizeOutput()` | Single-quoted eval, added sanitizeOutput |
| 4 | `150c555` | `meta.yml` still had old `echo $()` pattern | Updated meta.yml to match main.nf |
| 5 | `90b5a23` | **pre-commit prettier** + **Conda version robustness** | Single-quoted YAML + `python -c import` pattern |

---

## Issues Encountered & Root Causes

### Issue 1: `eval()` Quoting (Conda CI Crash)

**Symptom:** `bash: syntax error near unexpected token '('` in Conda CI.

**Root Cause:** The `echo $()` wrapper captured Python (Click) traceback output containing parentheses. Bash interpreted the `(` as syntax.

**Fix:** Use single-quoted `eval('...')` with direct pipe — no `echo $()` subshell.

**Lesson:** Never wrap `eval()` commands in `echo $()`. Python CLIs using Click can emit tracebacks to stderr that break bash parsing.

---

### Issue 2: `sanitizeOutput()` Missing

**Symptom:** Reviewer (@famosab) flagged raw `snapshot(process.out)` as non-compliant.

**Root Cause:** Topic channels add volatile version tuples to `process.out`. Without `sanitizeOutput()`, snapshots include numbered keys (`"0":`, `"1":`) alongside named keys (`"tsv":`, `"versions_emmtyper":`).

**Fix:** Wrap all snapshot assertions with `sanitizeOutput(process.out)`.

**Lesson:** **Every** nf-core test must use `sanitizeOutput()` from `nft-utils`. This is not optional.

---

### Issue 3: `meta.yml` Out of Sync

**Symptom:** Reviewer (@SPPearce) flagged that `meta.yml` still contained the old `echo $()` pattern after we fixed `main.nf`.

**Root Cause:** `meta.yml` has its own copy of the eval expression under both `output:` and `topics:` sections. Fixing `main.nf` alone is insufficient.

**Fix:** Always run `nf-core modules lint --fix` after changing `main.nf` — it auto-regenerates `meta.yml` from the process definition.

**Lesson:** `meta.yml` is a **derived artifact**. Never hand-edit it — always let `lint --fix` generate it.

---

### Issue 4: Prettier Formatting

**Symptom:** pre-commit CI failed with `prettier` reformatting `meta.yml` YAML strings.

**Root Cause:** We used `"escaped \"double\" quotes"` in YAML, but prettier normalizes to `'single quotes with "doubles" inside'`.

**Fix:** Run `npx prettier --check` locally before pushing. Or better: let `lint --fix` generate the meta.yml (it produces prettier-compatible output).

**Lesson:** Add `npx prettier --check modules/nf-core/<module>/meta.yml` to the local validation checklist.

---

### Issue 5: Python `--version` vs `python -c import`

**Symptom:** Seqera AI flagged that `emmtyper --version` output format differs between Docker and Conda due to Click version differences.

**Root Cause:** Click 7 writes `emmtyper v0.2.0` to stderr. Click 8 writes `emmtyper, version 0.2.0` to stdout. The `sed` pattern matches only one format.

**Fix:** Use `python -c "import emmtyper; print(emmtyper.__version__)"` — works identically in both environments.

**Lesson:** For **Python/Click-based tools**, prefer `python -c "import pkg; print(pkg.__version__)"` over CLI `--version | sed`. For compiled tools (C/Rust), the `--version | sed` pattern is fine.

---

### Issue 6: EDAM Ontology Comments Stripped by `lint --fix`

**Symptom:** Maintainer (@mribeirodantas) flagged that `# TSV` comment was missing from the EDAM ontology line in `meta.yml`.

**Root Cause:** `nf-core modules lint --fix` regenerates `meta.yml` via Python YAML serialization, which discards all inline comments. Over 1,055 modules in the repo use EDAM comments.

**Fix:** Created `restore_edam_comments.sh` script that diffs against `upstream/master` and restores stripped comments. Run it after `lint --fix`.

**Lesson:** YAML comments are not part of the data model — any round-trip through a YAML parser will strip them. Always run `restore_edam_comments.sh` after `lint --fix`.

---

## Validated Local Checklist (Pre-Push)

Every module PR must pass ALL of these before pushing:

```bash
# 1. Auto-fix meta.yml from main.nf (ALWAYS run first)
nf-core modules lint <module> --fix

# 2. Restore EDAM ontology comments (lint --fix strips YAML comments)
restore_edam_comments.sh <module>

# 3. Lint (must be 0 failures)
nf-core modules lint <module>

# 4. Prettier (must match CI's formatter)
npx prettier --check modules/nf-core/<module>/meta.yml

# 5. Tests (must pass and be stable)
nf-core modules test <module> --update --profile docker

# 6. Seqera AI review (optional but recommended)
seqera ai --headless --approval-mode basic \
  "Review modules/nf-core/<module>/main.nf for topic channel, stub, and eval correctness"
```

---

## Module Migration Template (for the next 39)

```bash
# 1. Create branch
git checkout -b stub-topics-<module> upstream/master

# 2. Edit main.nf
#    - Add topic channel output (use python -c for Python tools, --version|sed for compiled)
#    - Remove versions.yml output and HEREDOC
#    - Add stub: block

# 3. Auto-fix meta.yml
nf-core modules lint <module> --fix

# 4. Restore EDAM comments stripped by lint --fix
restore_edam_comments.sh <module>

# 5. Edit tests/main.nf.test
#    - Add sanitizeOutput() to existing test
#    - Add stub test case

# 6. Regenerate snapshots
nf-core modules test <module> --update --profile docker

# 7. Validate locally
nf-core modules lint <module>         # 53/53, 0 failures
npx prettier --check modules/nf-core/<module>/meta.yml  # All matched
nf-core modules test <module> --profile docker          # All passed

# 7. Seqera AI review (optional)
seqera ai --headless --approval-mode basic \
  "Review modules/nf-core/<module>/main.nf for correctness"

# 8. Commit & push (human gate)
git add modules/nf-core/<module>/
git commit -m "feat(<module>): Add stub block and migrate to topic channels"
git push origin stub-topics-<module>

# 9. Create PR (human gate)
```

---

## Documents Updated

All lessons from this retrospective have been propagated to:

| Document | Changes |
|---|---|
| [README.md](../README.md) | Python import pattern, 5-step pre-push checklist, Seqera AI QA section |
| [nf-core-contribution.md](../../../.agents/workflows/nf-core-contribution.md) | 5 new anti-patterns (#7-11), full pre-push checklist, meta.yml as derived artifact |
| [pr_split_strategy.md](../issues/4570-add-stub-blocks/pr_split_strategy.md) | `sanitizeOutput()` in test template, superseded PRs note, 5 new anti-patterns |
| [seqera-ai-subagent SKILL.md](../../../.agents/skills/seqera-ai-subagent/SKILL.md) | Pattern 6: Module QA Review with validated catches |
