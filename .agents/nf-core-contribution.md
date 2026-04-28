---
description: The end-to-end protocol for making open-source contributions to nf-core repositories. Covers issue selection, local development, lint compliance, and the gated PR submission pipeline with mandatory human approval at every externally-visible step.
---

# nf-core Open-Source Contribution Protocol

**Purpose:** Codifies the full lifecycle for contributing fixes and features to nf-core repositories (modules, pipelines, subworkflows). This workflow enforces nf-core's AI/LLM policy, the project's Git guardrails (GEMINI.md), and lessons learned from the Issue #5409 hackathon remediation.

**Reference Material:**
- nf-core Contributing Conventions: `docs/nextflow/reference/nfcore_contributing_reference.md` §A–L
- Prior Execution Retrospective: `docs/nextflow/walkthroughs/2026-04-26_nf_core_hackathon_full_lifecycle.md`
- Issue Artifacts: `docs/nextflow/issues/`

---

## Phase 1: Issue Selection & Scoping

### 1.1 Identify the Target Issue

Use the GitHub MCP tools to search for open issues in the target repository:

```
mcp_github-mcp-server_search_issues(query="is:open label:bug", owner="nf-core", repo="modules")
```

Alternatively, ingest project board items using GraphQL pagination (see `docs/nextflow/tools/scripts/ingest_hackathon_issues.py` for reference).

### 1.2 Scope Validation

**CRITICAL — Lessons Learned:** The swarm MUST constrain its work to the **exact scope defined in the issue**. Do NOT extend the fix to related-but-out-of-scope patterns. Over-scoping produces valuable diffs but creates PR pushback.

Verify scope by:
1. Reading the issue body, including the exact `git grep` or search command used to identify affected files
2. Cross-referencing the issue's module checklist against the current `master` branch — modules may have been fixed by other PRs since the issue was filed
3. Identifying any modules that were **added to the repo after the issue was filed** — the issue checklist may not include them

If out-of-scope improvements are discovered, document them separately in a `BUCKET_ANALYSIS.md` for a future companion issue. Do NOT mix scopes in a single PR.

### 1.3 Read nf-core Conventions

Before writing any code, the agent MUST read the nf-core contributing conventions documented in `docs/nextflow/implementation_plan.md` (§A–L). Key constraints:

| Rule | Source |
|---|---|
| PRs must be small and focused — no scope creep | nf-core AI/LLM Policy §A |
| No unnecessary changes (refactoring, style) beyond the fix | nf-core AI/LLM Policy §A |
| Humans are ultimately responsible for submitted code | nf-core AI/LLM Policy §A |
| `master` is the PR target for `nf-core/modules` | Branching Conventions §B |
| `dev` is the PR target for pipeline repos | Branching Conventions §B |
| Stub `.gz` files MUST use `echo "" | gzip >` (double quotes) | Stub Block Rules §F + Linter |
| All optional params go in `$args` via `ext.args` | Module Conventions §I |

> **HARD LESSON:** The nf-core linter (`nf-core modules lint`) enforces `echo "" | gzip >` with **double quotes**. Single quotes (`echo ''`) will fail the `test_stub_gzip_syntax` lint check. This convention is NOT documented in the contributing guide — it exists only in the linter source code.

---

## Phase 2: Local Development

### 2.1 Clone the Target Repository

Clone `nf-core/modules` (or the target repo) to a temporary working directory. Do NOT clone into the project workspace — use `/tmp/` to keep the workspace clean:

```bash
git clone --depth 1 https://github.com/nf-core/modules.git /tmp/nf-core-modules
```

### 2.2 Analyze Affected Modules

Write a script to programmatically identify affected modules. Stage the script in `.staging/` or `docs/nextflow/tools/scripts/`. The script should:

1. Use `git grep` with the exact pattern from the issue
2. Parse each module's `main.nf` to locate the `stub:` block
3. Generate `unified_diff` patches for each affected module
4. Produce structured reports (inventory, diffs, validation)

Reference implementation: `docs/nextflow/tools/scripts/process_modules.py`

### 2.3 Generate & Validate Diffs

Store individual `.diff` files in a clearly named directory structure per issue:

```
docs/nextflow/issues/NNNN-issue-name/
├── diffs/                  # Issue-scoped fixes (PR-ready)
├── reports/                # Validation and inventory reports
├── implementation_plan.md  # Scope split rationale and execution plan
└── directive.md            # Generated instructions
```

### 2.4 TDAID Validation

Write pytest assertions to validate the generated reports and diffs. At minimum:

1. Reports exist and contain expected sections
2. Diffs do NOT contain the original anti-pattern in `+` lines
3. Module count matches expectations

Run via `mcp_tdaid-ast-validation_execute_tdaid_test`.

---

## Phase 3: Director Handoff & Git Operations

**CRITICAL CONSTRAINT:** The autonomous swarm is **strictly forbidden** from executing any Git commits, pushes, or GitHub API mutations (e.g., creating PRs, forking). The swarm's scope is strictly bounded to Research and Engineering (Phase 1 & 2).

Once local diffs and TDAID validation are complete, the swarm MUST halt and hand off execution to the **Director** (Human User + Antigravity IDE). 

The Director will then manually execute the following steps with strict oversight. **Do NOT instruct the swarm to perform these steps:**

### GATE 1: Report Review
Present the completed reports, diff summaries, and bucket analysis to the Director. The Director will manually review the analysis.

### GATE 2: Fork Creation
The Director manually forks the target repository to the user's GitHub account using the GitHub CLI:
```bash
gh repo fork nf-core/modules --clone=false --remote=false
```

### GATE 3: Push Branch
The Director clones the fork, creates a descriptive branch, applies the generated diffs, and commits.
```bash
cd /tmp/nf-core-modules-fork
git checkout -b fix-<descriptive-name>
git remote add upstream https://github.com/nf-core/modules.git
# Apply diffs generated by the swarm
git add -A
git commit -m "fix(modules): <descriptive message>

Fixes #NNNN. <concise explanation>"
git push origin <branch-name>
```

### GATE 4: Create Draft PR
The Director manually creates a **Draft** PR against the target branch using the GitHub CLI.
```bash
gh pr create \
  --repo nf-core/modules \
  --base master \
  --head <user>:<branch-name> \
  --draft \
  --title "fix(modules): <title>"
```

### GATE 5: Lint Remediation
The Director monitors CI and fixes lint failures. If lint failures are caused by the change, they fix them locally and force-push.

### GATE 6: Ready for Review
The Director manually converts the Draft PR to "Ready for Review" in the GitHub UI.

---

## Phase 4: Post-Submission

### 4.1 Monitor Review Feedback
The Director checks for reviewer comments.
- **Snapshot updates:** Run `nf-core modules test <module> --update` locally, commit the new `.snap` files.
- **Formatting fixes:** Comment `@nf-core-bot fix linting`.

### 4.2 Companion Issues
If out-of-scope improvements were identified by the swarm, the Director prepares and submits a companion issue.

### 4.3 Documentation
The Swarm is re-engaged to write a retrospective in `docs/nextflow/walkthroughs/` covering:
- What the swarm did well during Phase 1 & 2
- What broke and how it was fixed
- Open work for future contributions

---

## Anti-Patterns & Hard Lessons

1. **DO NOT extend scope beyond the issue.** If you find related problems, document them in `BUCKET_ANALYSIS.md` for a companion issue. Do not mix scopes in one PR.
2. **DO NOT use single quotes in gzip stubs.** The nf-core linter enforces `echo "" | gzip >` (double quotes). This is not documented anywhere except the linter source — but it WILL fail CI.
3. **DO NOT fix pre-existing lint failures.** If a module already fails lint on `master` for unrelated reasons, document it in a PR comment. Fixing it is scope creep.
4. **DO NOT assume the issue checklist is current.** Cross-reference against the live `master` branch.
5. **DO NOT clone into the project workspace.** Use `/tmp/` for fork clones to avoid polluting the local repo.
6. **DO NOT execute Git/GitHub mutation operations.** The swarm is strictly a research and engineering tool. All commits, pushes, and PR creations must be executed manually by the Director.