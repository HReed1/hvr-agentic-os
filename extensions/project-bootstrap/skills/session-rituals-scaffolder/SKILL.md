---
name: session-rituals-scaffolder
description: Generates domain-tailored session-start and session-wrapup rituals with grounding steps, Cadence queries, endpoint discovery, retrospective prompts, drift checks, and local git protocol.
---

# Session Rituals Scaffolder

> **Domain:** Human-Agent Interaction & Cadence Rituals  
> **Purpose:** Generate domain-tailored `session-start` and `session-wrapup` agent skills, establishing structured bookends for all working sessions.

## Session Start Ritual Architecture (`session-start`)

1. **Step 0: Grounding & Governance**:
   Mandates inspecting `wiki/overview.md`, `.agents/rules/`, and operational concept guides before planning or executing tasks.
2. **Step 0.5: Knowledge Base Sync**:
   Executes `python3 scripts/export_wiki.py && python3 scripts/sync_wiki_db.py` to ensure local markdown files and the PostgreSQL knowledge index are in parity, asserting 0 orphans.
3. **Steps 1-3: Cadence Sprint & Milestone Review**:
   Queries Firestore collection `{{firestore_collection}}` for:
   - Incomplete daily goals from previous sessions (prompting to roll over, defer, or complete).
   - Active weekly sprint deliverables and progress bars.
   - Monthly strategic milestone alignment.
4. **Step 4: Environmental & Endpoint Discovery**:
   Probes live storage mounts (`/Volumes/*`, `~/Library/CloudStorage/*`) or local microservice ports, detects uncataloged endpoints, and flags differences against `ledger/drives.yaml`.
5. **Steps 5-6: Session Focus & Goal Activation**:
   Prompts creator for today's primary objective, creates a daily goal in Cadence with proper phase classification, and activates it (`status: in_progress`).

## Session Wrapup Ritual Architecture (`session-wrapup`)

1. **Step 1: Goal Accounting**:
   Marks completed daily goals, updates phases in Cadence, or defers unfinished goals with clear rationale.
2. **Step 2: Optional Retrospective Prompt**:
   Explicitly asks creator: *"Would you like to write a session retrospective in wiki/retro/?"*. If approved, authors a structured retrospective using `templates/_template_retro.md`.
3. **Step 3: Drift Check & Controlled Stamping**:
   Executes `python3 scripts/drift_enforcer.py` to assert dependency integrity. If verified changes occurred, prompts creator before executing `--stamp`.
4. **Step 4: Database Synchronization**:
   Runs wiki export and database sync to re-index any new retrospective or entity pages into PostgreSQL (`repo = '{{postgres_repo_key}}'`), verifying 0 orphans.
5. **Step 5: Local Git Protocol & Guardrails**:
   Reviews `git status` and diffs, verifies local-only git guardrails (strictly no unauthorized remote pushes), stages modified files, and commits with conventional format.
6. **Step 6: Operational Log Update**:
   Appends a structured audit entry to `wiki/log.md`.
