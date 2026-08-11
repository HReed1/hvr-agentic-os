---
title: "Session Lifecycle"
date: 2026-08-11
category: entity
tags:
  - workflow
  - session-management
  - drift-enforcement
  - retrospectives
sources:
  - "[[.agents/workflows/session-start.md]]"
  - "[[.agents/workflows/session-wrapup.md]]"
  - "[[GEMINI.md]]"
last_ingested: 2026-08-11
---

The Session Lifecycle is a structured workflow system that governs how engineering sessions are initialized and torn down in the [[agentic-os]]. It replaces ad-hoc cold starts with a disciplined briefing-and-wrapup pattern that surfaces context, enforces [[drift-registry]] checks, compounds knowledge through retrospectives, and ensures no session ends without a documented record. It was introduced as **Pillar 3: Agnostic Session Lifecycle** in the v2.0.0 release.

## Session Start

Triggered by `/session-start`, the initialization workflow (`.agents/workflows/session-start.md`) executes five steps:

1. **Load Project Context** — Reads `wiki/overview.md` to establish the current project state: architecture, active systems, known risks, and recent changes. Surfaces any architectural shifts or open questions from the overview.
2. **Scan Recent Retrospectives** — Scans `docs/retrospectives/` for the two most recent entries by date prefix, looking for incomplete work, open questions, and known risks. Reports these as a session briefing.
3. **Surface Drift (Informational)** — Runs `python3 scripts/drift_enforcer.py` to check whether tracked files changed since the last session stamp. Drift at session start typically means manual edits or CI updates occurred outside the agent workflow — this is expected and healthy. **The session is not blocked by drift.**
4. **Set Session Focus** — Asks the user: "What's the focus for this session?"
5. **Confirm Session Started** — Delivers a structured briefing summarizing project context, carryover items, and drift status.

## Session Wrapup

Triggered by `/session-wrapup`, the teardown workflow (`.agents/workflows/session-wrapup.md`) executes six steps:

1. **Stage and Commit** — Stages all modifications with `git add .` and generates a Conventional Commit message. Does **not** push to remote unless explicitly requested.
2. **Enforce Drift Checks and Stamp** — This is the **single correct stamping point** per session. Runs the drift enforcer, reviews flagged files for intentional changes, and stamps the new baseline with `--stamp`. Mid-session drift is expected and should never be stamped early.
3. **Generate Retrospective** — Creates a markdown file in `docs/retrospectives/` named `YYYY-MM-DD_brief_description.md` containing: context/objective, key accomplishments, files modified, drift report, decisions/gotchas, and carryover items.
4. **Wiki Ingest (Optional)** — For architecturally significant sessions only. Updates existing wiki pages, creates new pages if needed, updates `wiki/index.md` and `wiki/log.md`, and syncs the wiki database via `wiki_db_backfill.py`. Routine bug-fix sessions skip this step.
5. **Commit Documentation** — Stages and commits retrospectives, wiki updates, and stamped registries in a separate docs commit.
6. **Cleanup** — Deletes the ephemeral session drift log (`.agents/logs/session_drift.log`) and confirms completion to the user.

## Rules

Four inviolable rules govern the session lifecycle:

| Rule | Rationale |
|------|-----------|
| **Never stamp drift registries mid-session** | Stamping happens only in the wrapup workflow. Mid-session drift is expected — it means the enforcer is working. |
| **Always generate a retrospective** | Even short sessions get a retro. Future sessions depend on these for [[ephemeral-memory-handoff]] context. |
| **Don't push to remote automatically** | The user decides when to push. Agents never auto-push. |
| **Wiki ingest is optional** | Only ingest for architecturally significant sessions. Routine sessions skip it to avoid wiki noise. |

## Retrospective Format

Every retrospective in `docs/retrospectives/` follows a standard structure:

- **Context/Objective** — What was the session goal?
- **Key Accomplishments** — Bulleted list of completed work
- **Files Modified** — The main files changed
- **Drift Report** — Drift detected, whether it was stamped, and why it was safe
- **Decisions/Gotchas** — Design decisions or roadblocks encountered
- **Carryover** — Incomplete items for the next session

These retrospectives serve as the primary input to the session-start workflow's carryover scan, creating a self-reinforcing loop that combats the [[amnesia-sweep]] problem.

## History

The Session Lifecycle was formalized as part of v2.0.0's Pillar 3 (Agnostic Session Lifecycle), designed to work identically across Cursor, Claude Code, and Antigravity IDE. It depends on the [[drift-registry]] for enforcement and feeds into [[ephemeral-memory-handoff]] through its retrospective chain.

## See Also

- [[agentic-os]] — Parent system architecture
- [[drift-registry]] — Drift enforcement consumed during both start and wrapup
- [[ephemeral-memory-handoff]] — Retrospectives enable context transfer across sessions
- [[amnesia-sweep]] — The failure mode that structured sessions prevent
