# Pillar 4: Elephant-Goldfish Epistemic Verification

> **Portable AI Engineering Reference Guide (`docs/reference/elephant-goldfish-verification.md`)**
> Companion to [`llm-wiki-antigravity.md`](./llm-wiki-antigravity.md), [`drift-registry.md`](./drift-registry.md), and [`session-workflows.md`](./session-workflows.md).

---

## 1. The Problem: Why Single-Context Agents Glaze Their Own Drafts

The first three pillars of the AI Engineering Scaffold (**LLM Wiki** in [`llm-wiki-antigravity.md`](./llm-wiki-antigravity.md), **Drift Registry** in [`drift-registry.md`](./drift-registry.md), and **Session Workflows** in [`session-workflows.md`](./session-workflows.md)) solve **temporal amnesia across sessions**—preventing your agent from starting cold when a chat window closes or breaking cross-file contracts when code changes.

However, a second failure mode happens **inside a single session**:

As your primary orchestrator agent (**The Elephant**) accumulates deep session context over 30–60 turns of brainstorming, debugging, and drafting, its context window becomes a **self-reinforcing echo chamber**:
1. **The Curse of Knowledge:** When the Elephant writes an implementation plan (`docs/decisions/*.md`) or documentation page (`wiki/**/*.md`), it leaves out critical assumptions because those details were already discussed in earlier chat turns.
2. **Self-Review Blindness:** If you ask the same Elephant agent to *"review this specification for gaps"*, it reads the document using the very conversational memory that produced it—mentally filling in the missing pieces and declaring the draft ready.
3. **RLHF Sycophancy ("Glazing"):** Instruction-tuned models default to validating the user's premise (*"That's a brilliant architecture!"*) rather than attacking YAGNI violations, hidden operational costs, or uncalibrated claims.

---

## 2. The Solution: Elephant vs. Goldfish Context Separation

Inspired by Google's open-source **Elephant-Goldfish Model (`EGM`)** and unified with our stateful scaffold, we separate **deep-context authoring** from **zero-context verification**:

* **The Elephant (Primary Session Agent):** Holds the full session context, loads the `wiki/` overview and `Cadence` goals at `/session-start` (see [`session-workflows.md`](./session-workflows.md)), interviews the human engineer, and writes specifications or code changes to disk.
* **The Goldfish (Stateless Read-Only Subagents):** Fresh, read-only subagent invocations that receive **zero conversation history** and read **only** the target file on disk (plus explicitly bounded ground-truth files). Because a Goldfish has no memory of what the Elephant *meant* to write, it evaluates only what is *actually written*.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE ELEPHANT (Primary Agent)                         │
│  • Holds deep session context, Cadence goals, and Wiki state            │
│  • Drafts specification to disk (`docs/decisions/YYYY-MM-DD-spec.md`)   │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ Spawns 3 stateless read-only subagents
                                    │ (ZERO chat history passed)
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│  1. Comprehension │     │ 2. Critic/Zoom-Out│     │   3. Readiness    │
│     Goldfish      │     │     Goldfish      │     │     Goldfish      │
│ • Reads ONLY spec │     │ • Heilmeier &     │     │ • Audits code/AST │
│ • Naive-Reader    │     │   YAGNI critique  │     │   ground truth    │
│   Paraphrase Test │     │ • DROP/CALIBRATE  │     │ • Zero-Decision   │
└─────────┬─────────┘     └─────────┬─────────┘     └─────────┬─────────┘
          └─────────────────────────┼─────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  CHECKABLE RESOLUTION GATE (CONTEST | ESCALATE | PROPOSE FIX | DECLINE) │
│  • Elephant cannot dismiss findings with "this was intentional"         │
│  • Every CONTEST must cite a file/line the Goldfish could read          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Two-Track Triage Taxonomy (Controlling Token & Latency Cost)

Spawning subagents on every one-line bug fix wastes tokens and slows engineering velocity. Route every task into one of two mutually exclusive tracks:

| Track | Mutually Exclusive Scope Definition | Verification Mechanism | Subagent Cost |
| :--- | :--- | :--- | :--- |
| **Track 1: Routine Code or Docs Update** | Touches `<= 100` total changed lines **AND** `<= 2` files, and does **not** create or modify architectural specs (`docs/decisions/*.md`). | Deterministic Python/AST Harnesses: `drift_enforcer.py` (see [`drift-registry.md`](./drift-registry.md)), `pytest`, linter/typecheck gates. | **0 Subagents** (`< 1s` local check) |
| **Track 2: Architectural Spec, Multi-File Refactor, or Semantic Drift Audit** | Touches `> 100` total changed lines **OR** `>= 3` files, creates/modifies a design spec (`docs/decisions/*.md`), or audits a drifted contract prior to `drift_enforcer.py --stamp`. | **Artifact-First Drafting** + **3-Goldfish Subagent Gate** ([`/goldfish-review`](../../.agents/skills/goldfish-review/SKILL.md)) + Human Sign-Off Gate. | **3 Parallel Read-Only Subagents** (or 1 in `Mode: DRIFT_AUDIT`) |

### Key Track 2 Mechanisms Defined
- **Artifact-First Drafting:** Before writing multi-file application code (`> 100` lines or `>= 3` files) or invoking `/goldfish-review`, the Elephant must persist the specification or target document to disk (`docs/decisions/YYYY-MM-DD-feature-name-implementation-plan.md`). Never pass inline chat prose as the review target.
- **`/goldfish-review` ([`.agents/skills/goldfish-review/SKILL.md`](../../.agents/skills/goldfish-review/SKILL.md)):** The orchestration skill that spawns the stateless Goldfish subagents in parallel and collects their findings into a checkable resolution table.

---

## 4. The 3 Stateless Goldfish Personas (`.agents/personas/`)

### 4.0 Document Structure & Severity Scale
- **How `FeatureRange` and `DetailedRange` Are Delimited (Design Specs):** Every Track 2 architectural specification (`docs/decisions/*.md`) is split by the literal Markdown heading `## Detailed Implementation Plan` into two regions:
  - **`FeatureRange` (Above `## Detailed Implementation Plan`):** High-altitude objectives, Heilmeier Catechism, system architecture, and dispositioned alternatives (where each rejected option is marked with the literal string `Rejected by author: <concrete reason>`).
  - **`DetailedRange` (From `## Detailed Implementation Plan` downward):** Explicit `[CREATE]` / `[MODIFY]` / `[DELETE]` file allowlist, zero-decision execution steps, and verification commands.
  - *(Note: When auditing a `wiki/` or `README.md` file in `Mode: DRIFT_AUDIT`, the target document is a reference page rather than an implementation plan, so no `## Detailed Implementation Plan` heading is required).*
- **4-Tier Finding Severity Scale:** Every Goldfish persona classifies its findings into one of four severities:
  - `🔴 Blocker` — Contradicts codebase ground truth, fails the Naive-Reader Paraphrase Test, leaves an open architectural decision in `DetailedRange`, or introduces a severe security/correctness flaw.
  - `🟡 Major` — Significant ambiguity, unstated prerequisite, YAGNI over-engineering, or uncalibrated claim.
  - `🟢 Minor` — Structural friction, missing cross-reference link, or altitude bleed between `FeatureRange` and `DetailedRange`.
  - `💡 Nit` — Purely stylistic or wording polish that does not affect comprehension or correctness.

### 4.1 `goldfish-comprehension.md` ([`.agents/personas/goldfish-comprehension.md`](../../.agents/personas/goldfish-comprehension.md))
- **Context Boundary:** Reads **only** `TargetFile` (zero chat history, zero external repository files).
- **The Paraphrase Test:** Must begin its output with two exact 3–5 sentence sections:
  1. `### Paraphrase: What This Document Proposes`
  2. `### Paraphrase: How the Current System Works (Per This Document)`
- **Why It Works:** If the Goldfish's paraphrase contradicts the Elephant's intent—or if the Goldfish cannot paraphrase a mechanism without guessing—that section is automatically flagged as a `🔴 Blocker`. No amount of self-review by the Elephant can replicate a cold reader attempting to summarize the text back to you.

### 4.2 `goldfish-critic.md` ([`.agents/personas/goldfish-critic.md`](../../.agents/personas/goldfish-critic.md))
- **Context Boundary:** Reads `TargetFile` (`FeatureRange`) + explicitly linked `wiki/` context pages.
- **Operating Modes & Standards:**
  - **`Mode: BRAINSTORM` (Optional Pre-Spec Single-Subagent Pass):** Invoked during early problem exploration before `DetailedRange` is written. Attacks the hypothesis across 4 lenses: (1) Contrarian/YAGNI, (2) Maintenance/Token/Infrastructure Cost, (3) Failure Modes & Rollback, and (4) Unweighed Alternatives.
  - **`Mode: REVIEW` (Default Mode in the 3-Goldfish Spec Gate):** Audits `FeatureRange` against three standards:
    1. **Heilmeier Catechism:** Verifies the spec answers DARPA's classic design questions (*What is being attempted? What are the limits of current practice? What is new and why will it succeed? What are the risks/costs? What are the mid-term and final verification exams?*).
    2. **Zoom-Out Standard:** Verifies the design solves the root cause rather than a symptom and keeps low-level code weeds out of `FeatureRange`.
    3. **Style Claim Calibration (`[DROP]` | `[CALIBRATE]` | `[RELOCATE]` | `[KEEP]`):** Audits superlatives and defensive disclaimers:
       - `[DROP]`: Delete filler, sycophantic glazing, or redundant CYA disclaimers.
       - `[CALIBRATE]`: Bound overstated claims (e.g., *"guarantees zero bugs"*) to what the mechanism actually verifies.
       - `[RELOCATE]`: Move low-level implementation weeds from `FeatureRange` into `DetailedRange` (or vice versa).
       - `[KEEP]`: Retain concrete claims backed by a specific mechanism or metric.

### 4.3 `goldfish-readiness.md` ([`.agents/personas/goldfish-readiness.md`](../../.agents/personas/goldfish-readiness.md))
- **Context Boundary:** Reads `TargetFile` + inspects actual workspace files (`src/`, `api/`, `scripts/`, `tests/`).
- **Operating Modes & Standards:**
  - **Standard Spec Audit (Part of the 3-Goldfish Spec Gate):**
    1. **Code & Symbol Fact-Check:** Verifies every file path, function signature, CLI flag, and schema key cited as current state. **`Contradicts Code = 🔴 Blocker`**.
    2. **Zero-Decision Implementation Readiness:** Flags any step in `DetailedRange` that leaves an architectural, schema, or error-handling decision to the implementer.
  - **`Mode: DRIFT_AUDIT` (Single-Subagent Pre-Stamp Pass):** Invoked at `/session-wrapup` when `scripts/drift_enforcer.py` detects syntactic drift before running `drift_enforcer.py --stamp` (see [`drift-registry.md`](./drift-registry.md)). Compares the source file's `git diff` against its dependent `wiki/` or `README.md` documentation contract—checking **Interface** (signatures/flags), **Invariants** (constraints), **Side Effects** (DB/disk writes), and **Verification** (test commands).

---

## 5. Checkable Resolution Protocol (`CONTEST | ESCALATE | PROPOSE FIX | DECLINE`)

When the Goldfish subagents return their findings, the Elephant must assign one of four checkable dispositions to every item:

| Disposition | Rule & Evidence Required |
| :--- | :--- |
| **`PROPOSE FIX`** | Draft and apply the concrete text or code edit to `TargetFile` that resolves the finding. |
| **`CONTEST`** | Allowed **only** if the Elephant cites a specific file path and line/symbol that the Goldfish had access to read, proving the finding is factually incorrect. Never contest a finding with *"this was intentional"*. |
| **`ESCALATE`** | Required whenever the reason lives only in unwritten human context or requires the human author to choose between $\ge 2$ engineering trade-offs. |
| **`DECLINE`** | Allowed **strictly** for stylistic `💡 Nit` items that do not affect comprehension or correctness, with a 1-sentence rationale. (`🔴 Blocker`, `🟡 Major`, and `🟢 Minor` findings may never be `DECLINE`d). |

---

## 6. Constitutional Epistemic Hygiene Rules ([`.agents/rules/no-glazing-and-epistemic-hygiene.md`](../../.agents/rules/no-glazing-and-epistemic-hygiene.md))

Add the following invariants to your project's `AGENTS.md` / `GEMINI.md` and `.agents/rules/no-glazing-and-epistemic-hygiene.md`:
1. **No Glazing / Critique First:** Ban flattering adjectives (`"brilliant"`, `"great"`, `"smart"`, `"perfect"`, `"spot-on"`) and hollow apologies (`"I apologize"`, `"I'm sorry"`). Surface counter-arguments, hidden costs, and failure modes *before* affirming merits.
2. **Author Decides Trade-Offs:** When $\ge 2$ defensible options exist, present up to 3 options with their **mechanism, trade-offs, and failure conditions**, and ask the human author to decide.
3. **Two-Layer Hybrid Drift Enforcement:** Pair syntactic git SHA / AST hash checks (`scripts/drift_enforcer.py`) with semantic Goldfish contract verification (`goldfish-readiness` in `Mode: DRIFT_AUDIT`) prior to stamping at `/session-wrapup`.
