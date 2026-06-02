---
description: Automates end-of-session by committing changes, enforcing drift checks, generating a retrospective, and optionally ingesting significant work into the wiki.
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
   `YYYY-MM-DD_brief_description.md` (use the session date and a
   snake_case summary of the focus).
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
   - Source: `docs/retrospectives/YYYY-MM-DD_description.md`
   - Updated: [[entity-1]], [[entity-2]]
   - Created: [[new-page]] (if any)
   - Key insight: One-line summary of what this session added
   ```
7. Update the wiki database via the `wiki-db` MCP server.
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

> Do not push to remote unless explicitly requested by the user.

## Step 6: Final Report and Cleanup

1. Delete the session drift log (resets for next session):
   ```bash
   rm -f .agents/logs/session_drift.log
   ```
2. Confirm to the user:
   - Session changes committed
   - Drift evaluated (and stamped if necessary)
   - Retrospective generated and committed
   - Wiki updated (if applicable)
   - Any carryover items for the next session
