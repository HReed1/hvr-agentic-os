---
name: governance-architect
description: Generates constitutional agent governance documents (AGENTS.md, GEMINI.md, README.md) and modular domain safety rules (.agents/rules/) with two-tier universal and archetype-specific guardrails.
---

# Governance Architect

> **Domain:** Agent Constitutional Governance & System Invariants  
> **Purpose:** Generate legally binding agent constitutions, developer operation manuals, human orientation docs, and domain behavioral rules for newly bootstrapped workspaces.

## Constitutional Architecture (Two-Tier Model)

### Tier 1: Universal Constitutional Invariants
Installed on every workspace regardless of archetype:
1. **Strict Git Guardrails (Human Approval Required):**
   Explicit human approval required for pushing remotes, PRs, branch deletion, merging, and commenting. Local git operations are permitted.
2. **PostgreSQL Multi-Tenancy Boundary:**
   All queries and upserts against `localhost:5432/wiki` are strictly partitioned by `repo = '<project_slug>'`.
3. **Firestore Cadence Collection Isolation:**
   Goal management operations are restricted to `<project_slug>_goals` in Firestore `general-477613`.
4. **Error Sanitization & Secret Leak Prevention:**
   Never leak stack traces or internal secrets to API consumers or logs.
5. **Drift Enforcement & Stamping Discipline:**
   Stamping is strictly an end-of-session boundary marker during `/session-wrapup`.
6. **Context Engineering & AST Budgeting:**
   Prioritize AST inspection tools for resources > 100 lines.
7. **Implementation Plan Preservation & Semantic Split (`FeatureRange` vs. `DetailedRange`):**
   Plans remain in local artifact dir; archived plans use `YYYY-MM-DD-feature-name-implementation-plan.md` under `docs/decisions/` and enforce a strict semantic split between High-Altitude Architecture (`FeatureRange`: Heilmeier Catechism, Zoom-Out Standard, Alternatives with `Rejected by author: <reason>`) and Zero-Decision Implementation Plan (`DetailedRange`: explicit `[CREATE]`/`[MODIFY]`/`[DELETE]` file allowlist and zero open design choices).
8. **Epistemic Hygiene, Anti-Sycophancy & Elephant-Goldfish Verification (`no-glazing-and-epistemic-hygiene.md`):**
   - **No Glazing / Critique First:** Ban flattering filler adjectives (`"brilliant"`, `"great"`, `"smart"`, `"perfect"`, `"spot-on"`) and hollow apologies. Surface counter-arguments, hidden costs, and failure modes before affirming merits.
   - **Author Decides Trade-Offs:** When $\ge 2$ defensible options exist, present up to 3 options with mechanisms, trade-offs, and failure conditions; never pick silently on the human author's behalf.
   - **Two-Track Triage Taxonomy & 3-Goldfish Gate (`/goldfish-review`):** Track 1 routine updates (`<= 100` lines, `<= 2` files) use deterministic Python harnesses; Track 2 architectural specs (`docs/decisions/`) and high-stakes packets (`packets/`) spawn 3 stateless read-only Goldfish subagents (`goldfish-comprehension`, `goldfish-critic`, `goldfish-readiness`) resolved via checkable `CONTEST | ESCALATE | PROPOSE FIX | DECLINE` rules.

### Tier 2: Modular Archetype & Domain Invariants
Selected dynamically based on the project's archetype and task prompt:
- **`agentic_os`**: Agent firewalling, write budgets, prompt injection defense (`system_instruction` separation), tool sandboxing, deterministic state UUIDs.
- **`software_engineering`**: API zero-trust, timing-safe HMAC verification, replay protection, runtime secret injection, frontend DOM sanitization, CI/CD build gates.
- **`creative_operations`**: Zero-mutation on external volumes (`/Volumes/*`), FileProvider cloud non-hydration, 3-2-1 backup verification, master asset immutability.
- **`data_platform`**: Raw store immutability, PII/PHI privacy redaction, pipeline idempotency, schema validation.
- **`minimal_research`**: Source layer read-only immutability, strict claims attribution, contradiction surfacing.

## Documents Generated

- `AGENTS.md`: Mandatory agent constitution with Universal Core + Domain Invariants.
- `GEMINI.md`: Architecture manual, Cadence CLI recipes, SQL query cheatsheet.
- `README.md`: Human developer orientation, quickstart commands.
- `.agents/rules/`:
  - Universal rules: `git-guardrails.md`, `cadence-discipline.md`, `wiki-db-governance.md`, `drift-detection-governance.md`, `context-and-ast-governance.md`, `plan-preservation-governance.md`, `no-glazing-and-epistemic-hygiene.md`.
  - Archetype rules: Injected from `templates/rules/archetypes/<archetype>/`.
- `.agents/personas/` & `.agents/skills/goldfish-review/`:
  - Stateless read-only subagent personas (`goldfish-comprehension.md`, `goldfish-critic.md`, `goldfish-readiness.md`) and `/goldfish-review` orchestration skill.
