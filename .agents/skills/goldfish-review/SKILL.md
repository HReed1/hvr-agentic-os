---
name: goldfish-review
description: Orchestrates the 3-Goldfish stateless subagent verification gate (Comprehension, Critic/Zoom-Out, Readiness/Ground-Truth) via parallel read-only invoke_subagent calls, compiles a unified review report, and enforces the checkable CONTEST | ESCALATE | PROPOSE FIX | DECLINE resolution protocol.
---

# Skill: 3-Goldfish Stateless Subagent Verification Gate (`/goldfish-review`)

> **Architectural Purpose:** Breaks single-context conversational confirmation bias by spawning **3 fresh, stateless, zero-history, read-only subagents** (**The Goldfish**) to audit a staged specification (`docs/decisions/*.md`) or drifted documentation contract created by the primary session agent (**The Elephant**).

---

## 1. When to Invoke (`/goldfish-review`)

Use the **Two-Track Triage Taxonomy** to decide whether to run this skill:
- **Track 1 (Skip `/goldfish-review`):** Routine code or doc updates (`<= 100` changed lines **AND** `<= 2` files, not touching `docs/decisions/`). Use fast deterministic Python/AST harnesses (`drift_enforcer.py`, `pytest`) instead.
- **Track 2 (Mandatory `/goldfish-review`):**
  1. Any new or revised architectural specification or implementation plan (`docs/decisions/*.md` or artifact blueprint).
  2. Any multi-file refactor touching `> 100` changed lines **OR** `>= 3` files.
  3. **Semantic Drift Audit (`Mode: DRIFT_AUDIT`):** Prior to stamping `drift_enforcer.py --stamp` when a core script or module has drifted from its tracked `wiki/` or `README.md` contract.

---

## 2. Execution Protocol (4-Step Workflow)

### Step 1: Ensure Artifact-First Persisted Target (`TargetFile`)
Before spawning any Goldfish subagent, ensure the document under review is written to disk at an absolute path (`TargetFile`). Never pass inline chat text as the review target.

### Step 2: Parallel 3-Goldfish Fan-Out (`invoke_subagent`)
Spawn three parallel **read-only** `research` subagents (`Model: "inherit"`) using `invoke_subagent`. Each subagent starts with **zero conversation history** and reads its persona file from `.agents/personas/`:

1. **Subagent 1 — `Comprehension Goldfish`:**
   - `TypeName`: `"research"`
   - `Role`: `"Comprehension Goldfish Reviewer"`
   - `Prompt`:
     ```text
     Read and strictly follow the persona instructions in `.agents/personas/goldfish-comprehension.md`.
     Your TargetFile is `<ABSOLUTE_PATH_TO_TARGET_FILE>`.
     IMPORTANT: Read ONLY `.agents/personas/goldfish-comprehension.md` and `<ABSOLUTE_PATH_TO_TARGET_FILE>`. Do not read any other files in the workspace. Return the Naive-Reader Paraphrase Test followed by all Comprehension & Self-Containment findings.
     ```

2. **Subagent 2 — `Critic & Zoom-Out Goldfish`:**
   - `TypeName`: `"research"`
   - `Role`: `"Critic and Zoom-Out Goldfish Reviewer"`
   - `Prompt`:
     ```text
     Read and strictly follow the persona instructions in `.agents/personas/goldfish-critic.md` (`Mode: REVIEW` or `Mode: BRAINSTORM`).
     Your TargetFile is `<ABSOLUTE_PATH_TO_TARGET_FILE>`.
     You may also read the following linked context files if needed: `<OPTIONAL_EXPLICIT_WIKI_PATHS>`.
     Return your Heilmeier/Zoom-Out architectural critique and Style Claim Calibration (`DROP | CALIBRATE | RELOCATE | KEEP`) findings.
     ```

3. **Subagent 3 — `Readiness & Ground-Truth Goldfish`:**
   - `TypeName`: `"research"`
   - `Role`: `"Readiness and Ground-Truth Goldfish Auditor"`
   - `Prompt`:
     ```text
     Read and strictly follow the persona instructions in `.agents/personas/goldfish-readiness.md`.
     Your TargetFile is `<ABSOLUTE_PATH_TO_TARGET_FILE>`.
     Inspect the actual repository files referenced in `TargetFile` to verify every file path, symbol, schema key, and factual claim (`Contradicts Code = 🔴 Blocker`), and audit `## Detailed Implementation Plan` against the Zero-Decision Implementation Readiness Standard.
     ```

> **Reactive Wakeup Rule:** After invoking the subagents, do **not** poll in a loop. Wait for the system to deliver the subagent responses.

### Step 3: Checkable Resolution Table (`CONTEST | ESCALATE | PROPOSE FIX | DECLINE`)
Once all 3 Goldfish subagents return their reports, synthesize their findings into a single structured review section or artifact (`goldfish_review_report.md`):

1. **Evaluate the Comprehension Paraphrase First:** Compare `goldfish-comprehension`'s paraphrase of `### Paraphrase: What This Document Proposes` and `### Paraphrase: How the Current System Works (Per This Document)` against your actual intent. Any mismatch is a `🔴 Blocker` that requires clarifying the prose in `TargetFile`.
2. **Assign a Checkable Disposition to Every Finding:**
   - **`PROPOSE FIX`:** Apply or stage the exact edit to `TargetFile` that resolves the finding.
   - **`CONTEST`:** Allowed **only** when you cite a specific file path and line number/symbol that the Goldfish had access to read, proving the finding is factually wrong. Never contest a finding by appealing to unwritten chat history or saying *"this was intentional"*.
   - **`ESCALATE`:** Required whenever resolving the finding depends on unwritten human context or requires the human author to choose between $\ge 2$ trade-offs.
   - **`DECLINE`:** Allowed strictly for minor stylistic `💡 Nit` items, with a 1-sentence engineering reason (`🔴 Blocker`, `🟡 Major`, and `🟢 Minor` findings may never be `DECLINE`d).

### Step 4: Apply Non-Contested Fixes & Present Human Gate
1. Apply all `PROPOSE FIX` improvements directly to `TargetFile`.
2. Present a concise summary in chat linking to `TargetFile`, highlighting:
   - Whether the Naive-Reader Paraphrase succeeded,
   - How many `🔴 Blocker` / `🟡 Major` findings were fixed automatically, and
   - Any `ESCALATE` trade-off questions requiring the human author's decision.
