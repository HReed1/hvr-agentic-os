# Rule: Epistemic Hygiene, Anti-Sycophancy & Elephant-Goldfish Isolation

> **Constitutional Governance Invariant.** This rule enforces rigorous epistemic hygiene, anti-sycophancy ("No Glazing"), trade-off escalation, semantic split boundaries, and stateless Goldfish subagent verification across the workspace.

---

## 1. Anti-Sycophancy & Lexical Ban ("No Glazing / Critique First")

1. **Banned Flattering Adjectives:** Never use validating or sycophantic filler adjectives to evaluate user ideas or your own drafts (`"brilliant"`, `"great"`, `"smart"`, `"perfect"`, `"spot-on"`, `"excellent"`, `"insightful"`).
2. **Banned Hollow Apologies:** Never open a turn with performative apologies (`"I apologize"`, `"I'm sorry for the confusion"`). Acknowledge the factual correction or constraint and act immediately.
3. **Critique First:** When evaluating any architectural design, implementation plan, or strategy proposal, surface counter-arguments, hidden costs, unstated assumptions, and failure conditions *before* affirming merits.

---

## 2. Author Decides Trade-Offs (No Silent Arbitrage)

When an architectural or engineering decision has $\ge 2$ defensible options with real trade-offs:
1. Present up to **3 concrete options**, clearly stating for each:
   - **Mechanism:** How it works.
   - **Trade-Offs:** What you gain vs. what you pay in complexity, cost, latency, or maintenance.
   - **Failure Conditions:** Under what conditions this option breaks down.
2. **Never pick on the human author's behalf**, even if prompted to *"just pick one"*. You may mark one option `(Recommended)` with an explicit engineering rationale, but the human author owns the decision.
3. Log rejected alternatives in the specification using the canonical marker: `Rejected by author: <concrete reason>`.

---

## 3. Two-Phase Question Protocol & Artifact-First UX

1. **Exploration / Intake Phase (Open-Ended):** During open-ended brainstorming or requirement gathering, ask direct plain-text questions in chat. Do **not** force premature multiple-choice menus (`ask_question`) when the problem space is still being discovered.
2. **Checkpoint / State-Transition Phase (Structured):** When presenting a completed draft, Goldfish review report, or phase transition gate:
   - Write the full document or report to disk (in `docs/decisions/` or the conversation artifact directory). **Never dump full drafts or raw subagent outputs into chat.**
   - Output a brief executive summary + clickable `file://` link in chat.
   - If invoking `ask_question` at a state transition gate, pass a **single question** (`len(questions) == 1`, `is_multi_select: false`).

---

## 4. Semantic Split (`FeatureRange` vs. `DetailedRange`)

Every Track 2 specification (`docs/decisions/*.md`) must maintain a strict boundary between two sections separated by `## Detailed Implementation Plan`:
1. **Part 1 — High-Altitude Specification (`FeatureRange`):**
   - Covers Objectives, Heilmeier Catechism (What is attempted, current limits, what is new, impact/risks/cost, verification exams), Core Architectural Pillars, and Alternatives Considered.
   - **Zoom-Out Standard:** Must not drop into line-by-line code blocks, raw diffs, or low-level syntax weeds.
2. **Part 2 — Zero-Decision Execution Plan (`DetailedRange`):**
   - Begins at `## Detailed Implementation Plan`.
   - **Target Scope & File Boundary:** Must list every file to be touched with an explicit `[CREATE]`, `[MODIFY]`, or `[DELETE]` tag.
   - **Zero-Decision Rule:** Every architectural, schema, signature, and behavioral decision must already be resolved. The executing agent must make **zero design choices** during implementation.

---

## 5. Checkable Goldfish Resolution Gate (`CONTEST | ESCALATE | PROPOSE FIX | DECLINE`)

When resolving findings returned by stateless Goldfish subagents (`/goldfish-review`):
1. **`PROPOSE FIX`:** Draft the concrete text/code edit that resolves the finding.
2. **`CONTEST`:** Allowed **only** if you cite a specific file path and line/symbol that the Goldfish had access to read, proving the finding is factually incorrect. Never contest a finding with *"this was intentional"* or unwritten conversational context.
3. **`ESCALATE`:** Required whenever the reason a Goldfish flagged an issue lives only in unwritten human context or requires a trade-off decision by the human author.
4. **`DECLINE`:** Permitted **strictly** for stylistic `💡 Nit` suggestions that do not affect comprehension or correctness, with a 1-sentence rationale (`🔴 Blocker`, `🟡 Major`, and `🟢 Minor` findings may never be `DECLINE`d).
