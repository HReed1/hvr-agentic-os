---
description: Structured session initialization. Loads project context, surfaces outstanding work and drift, and sets session focus.
---

# Session Start

> **Trigger:** Run at the beginning of each engineering session via `/session-start`.
> **Purpose:** Replace cold starts with a structured briefing that surfaces
> context, sets focus, and catches drift before you write code.

## Step 1: Load Project Context

Read `wiki/overview.md` to establish the current project state. This gives
you a pre-compiled understanding of the architecture, active systems,
known risks, and recent changes — without re-reading raw documentation.

If `wiki/overview.md` mentions any recent architectural shifts, security
concerns, or open questions, surface them to the user as part of the
session briefing.

## Step 2: Scan Recent Retrospectives for Carryover

Scan `docs/retrospectives/` for the **2 most recent** entries (by date
prefix). Look for:
- **Incomplete work** — anything flagged as "deferred" or "next session"
- **Open questions** — design decisions that were postponed
- **Known risks** — issues flagged but not yet resolved

Report these to the user as a session briefing.

## Step 3: Surface Drift (Informational)

Run the drift enforcer to check if any tracked files have changed since
last session's stamp:

```bash
python3 scripts/drift_enforcer.py
```

If drift is detected, report which domains are affected and what files
need review. **This is informational — do not block the session**, but
make the user aware.

> **Note:** Drift at session start usually means files were changed
> outside the agent's workflow (manual edits, CI updates, dependency
> bumps). This is expected and healthy — the system is catching it.

## Step 4: Set Session Focus

Ask the user:
> "What's the focus for this session?"

Use the user's answer to understand scope and priorities for this session.

## Step 5: Confirm Session Started

Confirm the session is underway:
> "Session started. Focus: [user's stated focus]. Here's what I know:
> - [1-2 lines from wiki/overview.md context]
> - [Any carryover items from recent retros]
> - [Drift status: clean / N domains need review]
> Let's begin."
