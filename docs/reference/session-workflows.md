# Session Workflows

A pattern for structured engineering sessions with LLM agents — with automatic drift enforcement, retrospective generation, and wiki maintenance baked into the lifecycle.

This is an implementation guide. Copy this file into your project and tell your LLM agent to create the session-start and session-wrapup skills. The agent will create the workflow files and configure them for your project's directory structure.

> **Dependencies:** This guide integrates with the [Drift Registry](./drift-registry.md) and [LLM Wiki](./llm-wiki-antigravity.md) patterns. You can use session workflows standalone, but they're most powerful when all three systems reinforce each other.

## The problem

LLM agent sessions are ephemeral. The agent forgets everything between conversations. This creates three recurring failures:

1. **Cold starts.** Every session begins with the agent re-reading the codebase blind, missing recent context, incomplete work, and known risks.
2. **Silent drift.** Code changes during a session break implicit contracts between files — and nobody checks until it's too late.
3. **Lost knowledge.** Design decisions, debugging breakthroughs, and architectural shifts evaporate into chat history. The next session rediscovers the same things.

Session workflows solve all three by wrapping every engineering session in a structured open → work → close lifecycle.

## The core idea

**Session start** loads context before you begin: recent changes, outstanding work, known drift, and the project's current state from the wiki. You set a focus for the session, and the agent has everything it needs to be productive immediately.

**Session wrapup** captures context before it's lost: commit the work, enforce drift checks, generate a retrospective, and optionally ingest significant findings into the wiki. The next session's start workflow picks up exactly where this one left off.

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  /session-start │     │   Engineering    │     │ /session-wrapup  │
│                 │     │     Session      │     │                  │
│ • Load wiki     │────▶│                  │────▶│ • Commit work    │
│ • Check backlog │     │  Actual coding,  │     │ • Enforce drift  │
│ • Surface drift │     │  debugging, etc. │     │ • Gen retrospect │
│ • Set focus     │     │                  │     │ • Wiki ingest    │
└─────────────────┘     └──────────────────┘     └──────────────────┘
        ▲                                                 │
        │           Knowledge compounds across            │
        └─────────────────sessions─────────────────────────┘
```

## Directory structure

Session workflows live in the `.agents/workflows/` directory:

```
your-project/
├── .agents/
│   ├── workflows/
│   │   ├── session-start.md      # Start-of-session ritual
│   │   └── session-wrapup.md     # End-of-session ritual
│   └── logs/
│       └── session_drift.log     # Ephemeral per-session drift log (auto-deleted)
├── docs/
│   ├── retrospectives/           # Session retrospectives (one per session)
│   │   ├── 2026-06-01-auth-refactor.md
│   │   └── 2026-06-02-webhook-hardening.md
│   └── drift_registries/         # Drift registry JSON files
├── wiki/                         # LLM Wiki (optional but recommended)
└── scripts/
    └── drift_enforcer.py         # Drift enforcement script
```

## Session Start Workflow

Create this as `.agents/workflows/session-start.md`:

```markdown
---
name: session-start
description: Structured session initialization. Loads project context,
  surfaces outstanding work and drift, and sets session focus.
---

# Session Start

> **Trigger:** Run at the beginning of each engineering session.
> **Purpose:** Replace cold starts with a structured briefing that surfaces
> context, sets focus, and catches drift before you write code.

## Step 1: Load Project Context

Read `wiki/overview.md` to establish the current project state. This gives
you a pre-compiled understanding of the architecture, active systems,
known risks, and recent changes — without re-reading raw documentation.

If `wiki/overview.md` mentions any recent architectural shifts, security
concerns, or open questions, surface them to the user as part of the
session briefing.

> If the project doesn't have a wiki yet, read the most recent 2-3
> retrospectives in `docs/retrospectives/` instead.

## Step 2: Check Recent Retrospectives

Scan `docs/retrospectives/` for the most recent 1-2 entries. Look for:
- **Incomplete work** — anything flagged as "deferred" or "next session"
- **Open questions** — design decisions that were postponed
- **Known risks** — issues flagged but not yet resolved

Report these to the user as a session briefing.

## Step 3: Surface Drift

Run the drift enforcer to check if any tracked files have changed since
last session's stamp:

```bash
python3 scripts/drift_enforcer.py
```

If drift is detected, report which domains are affected and what files
need review. This is informational — don't block the session, but make
the user aware.

> **Note:** Drift at session start usually means files were changed
> outside the agent's workflow (manual edits, CI updates, dependency
> bumps). This is expected and healthy — the system is catching it.

## Step 4: Set Session Focus

Ask the user:
> "What's the focus for this session?"

Use the user's answer to understand scope and priorities for this session.

## Step 5: Start Session

Confirm the session is underway:
> "Session started. Focus: [user's stated focus]. Here's what I know:
> - [1-2 lines from wiki/overview.md context]
> - [Any carryover items from recent retros]
> - [Drift status: clean / N domains need review]
> Let's begin."
```

## Session Wrapup Workflow

Create this as `.agents/workflows/session-wrapup.md`:

```markdown
---
name: session-wrapup
description: Automates end-of-session by committing changes, enforcing
  drift checks, generating a retrospective, and optionally ingesting
  significant work into the wiki.
---

# Session Wrapup

> **Trigger:** Run when the user asks to "wrap up", "finish the session",
> or explicitly runs `/session-wrapup`.

## Step 1: Stage and Commit Session Changes

1. Stage all relevant modifications:
   ```bash
   git add .
   ```
2. Generate a concise Conventional Commit message summarizing the work
   (e.g., `feat: ...`, `fix: ...`, `chore: ...`).
3. Commit:
   ```bash
   git commit -m "<generated_commit_message>"
   ```

> Do not push to remote unless explicitly requested by the user.

## Step 2: Enforce Drift Checks

> [!IMPORTANT]
> **This is the single correct stamping point per session.** Do NOT stamp
> drift registries during active development. Drift detected mid-session
> is expected — it means the enforcer is working. Save stamping for this
> wrapup step to preserve the system as a genuine safety net.

1. Run the drift enforcer:
   ```bash
   python3 scripts/drift_enforcer.py
   ```
2. **If drift is detected:**
   - Review flagged files to ensure changes were intentional
   - If unexpected drift is found, stop and consult the user
   - Otherwise, stamp the new baseline:
     ```bash
     python3 scripts/drift_enforcer.py --stamp
     ```

## Step 3: Generate Retrospective

1. Review the work accomplished during the session.
2. Create a new markdown file in `docs/retrospectives/` named
   `YYYY-MM-DD-brief-description.md`.
3. Include:
   - **Context/Objective:** What was the goal?
   - **Key Accomplishments:** Bulleted list of what was achieved
   - **Files Modified:** The main files that were changed
   - **Drift Report:** Summarize any drift detected and resolved.
     Explain why it was safe to stamp.
   - **Decisions/Gotchas:** Important design decisions or roadblocks
   - **Carryover:** Anything left incomplete for the next session

## Step 4: Wiki Ingest (Significant Sessions Only)

> [!NOTE]
> **Skip this step** for routine bug-fix or chore sessions. Only ingest
> when the session involved architectural changes, new features, security
> work, or meaningful design decisions.

If the session was significant:

1. Read the just-generated retrospective.
2. Identify which existing wiki pages need updating.
3. Update relevant pages in `wiki/entities/` and `wiki/concepts/`:
   - Note where new work confirms, extends, or contradicts existing content
   - Add new source references to the page's `sources:` frontmatter
4. If a new system or pattern was introduced, create a new wiki page.
5. Update `wiki/index.md` with any new entries.
6. Append to `wiki/log.md`:
   ```markdown
   ## [YYYY-MM-DD] ingest | Session Retrospective: <description>
   - Source: `docs/retrospectives/YYYY-MM-DD-description.md`
   - Updated: [[entity-1]], [[entity-2]]
   - Created: [[new-page]] (if any)
   - Key insight: One-line summary of what this session added
   ```
7. Update `docs/drift_registries/wiki.json` with any new/modified wiki
   page entries.
8. Optionally update `wiki/overview.md` if the session changes the
   project's big picture.

## Step 5: Commit Documentation & Registries

1. Stage retrospective, wiki updates, and stamped registries:
   ```bash
   git add docs/ wiki/
   ```
2. Commit:
   ```bash
   git commit -m "docs: session retrospective, wiki updates, drift stamps"
   ```

## Step 6: Final Report

1. Delete the session drift log (resets for next session):
   ```bash
   rm -f .agents/logs/session_drift.log
   ```
2. Confirm to the user:
   - Session changes committed
   - Drift evaluated (and stamped if necessary)
   - Retrospective generated and committed
   - Wiki updated (if applicable)
```

## Agent schema protocol

Add this to your agent configuration file (`GEMINI.md`, `CLAUDE.md`, or `AGENTS.md`):

```markdown
## Session Lifecycle

This project uses structured session workflows.

### Starting a session
Run `/session-start` (or the workflow at `.agents/workflows/session-start.md`)
at the beginning of each engineering session. This loads project context,
surfaces carryover work, and checks for drift before you write any code.

### Ending a session
Run `/session-wrapup` (or `.agents/workflows/session-wrapup.md`) at the end
of each session. This commits work, enforces drift checks, generates a
retrospective, and optionally ingests significant work into the wiki.

### Rules
- **Never stamp drift registries mid-session.** Stamping happens only in
  the wrapup workflow.
- **Always generate a retrospective.** Even short sessions get a retro.
  Future sessions depend on these for context.
- **Don't push to remote automatically.** The user decides when to push.
- **Wiki ingest is optional.** Only ingest for architecturally significant
  sessions. Routine bug-fix sessions skip Step 4 of the wrapup.
```

## How the three systems reinforce each other

```
┌───────────────────────────────────────────────────────────┐
│                    SESSION START                           │
│                                                           │
│  wiki/overview.md ──────── Pre-compiled project context   │
│  docs/retrospectives/ ──── Carryover from last session    │
│  drift_enforcer.py ─────── Catch out-of-band changes      │
└───────────────────────────────────────────────────────────┘
                          │
                    [Engineering Work]
                          │
┌───────────────────────────────────────────────────────────┐
│                   SESSION WRAPUP                          │
│                                                           │
│  git commit ────────────── Snapshot the work              │
│  drift_enforcer.py ─────── Enforce cross-file contracts   │
│  docs/retrospectives/ ──── Capture decisions & context    │
│  wiki/ ─────────────────── Compound knowledge (if major)  │
│  drift --stamp ─────────── Reset baseline for next session│
└───────────────────────────────────────────────────────────┘
                          │
                    [Knowledge persists]
                          │
                    Next /session-start picks it all up
```

| System | Role in the lifecycle |
|--------|---------------------|
| **Drift Registry** | Catches broken contracts at session start (informational) and session end (enforced). Stamped only at wrapup. |
| **LLM Wiki** | Provides instant context at session start via `overview.md`. Receives significant findings at session end via retrospective ingest. |
| **Retrospectives** | Bridge between sessions. Written at wrapup, read at start. The wiki synthesizes patterns from individual retros. |

## Customization guide

The workflows above are intentionally minimal. Here's how to extend them for your project:

### If you use a task/goal tracking system
Add a step to session-start that queries your task system (Jira, Linear, Firestore, etc.) for incomplete items. Add a step to session-wrapup that marks completed items.

### If you have CI/CD
Add a step to session-wrapup that checks CI status after the commit. If CI fails, flag it in the retrospective as a carryover item.

### If you have multiple environments
Add a step to session-start that checks which environment is active (dev/staging/prod) and surfaces any deployment drift.

### If you want phase tracking
Add engineering phases to session-start (Planning → Engineering → Testing → Cleanup → Docs → Review) and track transitions in the retrospective.

## Bootstrap instructions

Tell your LLM agent:

> **"Set up session workflows for this project. Follow the guide in this file: [path to this file]. Create the session-start and session-wrapup workflows in `.agents/workflows/`, create the `docs/retrospectives/` directory, and add the Session Lifecycle section to [GEMINI.md|CLAUDE.md|AGENTS.md]."**

The agent should:
1. Create `.agents/workflows/session-start.md` and `session-wrapup.md`
2. Create `docs/retrospectives/` directory
3. Create `.agents/logs/` directory for the ephemeral drift log
4. Add the Session Lifecycle protocol to the agent configuration file
5. Verify the drift enforcer script exists (if using drift registry integration)
6. Verify `wiki/overview.md` exists (if using wiki integration)

## Common mistakes to avoid

1. **Stamping drift mid-session.** The whole point of the drift system is to catch unintended breakage. If you stamp after every file save, you've disabled it. Stamp once, at wrapup, after reviewing.

2. **Skipping the retrospective.** "Nothing important happened" is never true. Even a bug-fix session produces context (which file was buggy, why, how it was fixed) that prevents the next agent from debugging the same thing.

3. **Bulk-ingesting every retro into the wiki.** Not every session is architecturally significant. If you ingest routine debugging sessions, the wiki fills with noise. Ingest the retros that represent shifts — new systems, security hardening, architectural decisions, pattern changes.

4. **Pushing to remote automatically.** Let the user decide when to push. Some sessions produce work-in-progress that shouldn't be on `main` yet.

5. **Making session-start too heavy.** The start workflow should take 30-60 seconds, not 5 minutes. Load `overview.md`, scan recent retros, run the drift check, ask for focus — then go. Don't run full test suites or lint passes at start.

## Attribution

This pattern was developed for [hvr-informatics](https://github.com/harrisonreed/hvr-informatics), where session retrospectives and drift enforcement evolved from a manual discipline into an automated workflow. The session lifecycle integrates with the [LLM Wiki](./llm-wiki-antigravity.md) and [Drift Registry](./drift-registry.md) patterns to create a self-reinforcing knowledge system across engineering sessions.
