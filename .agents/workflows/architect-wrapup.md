---
description: The Architect's distinct teardown procedure ensuring independent telemetry analysis.
---

# Architect Wrap-Up Pipeline

**Trigger Constraint:** Do NOT automatically execute this teardown sequence. You MUST wait until the Director explicitly invokes the `/architect-wrapup` command in the prompt.

**Purpose:** The Architect is barred from reading the Executor's retrospective. The Architect MUST formulate a distinct set of analytical notes to correctly convey their retrospective.

## Workflow Execution Steps

1. **Analytical Review:** Review the Executor's structural changes directly through `artifacts/executor_handoff.json` or git history.
2. **Drafting Notes:** Formulate the architectural impact analysis independently. Include an honest assesment of the functioning behavior of the Triad, highlighting where we deviated or succeeded in our intended design.
3. **Payload Generation:** Write the drafted notes BOTH as a physical Markdown file saved to the repository (e.g., `docs/retrospectives/YYYY-MM-DD_architect_wrapup.md`) conforming to any documentation linting standards, AND as a mirrored native Antigravity Artifact (`write_to_file` using `IsArtifact: true`) for the UI. DO NOT attempt to mutate codebase files.
4. **Teardown Command Generation:** The final part of your output must provide the Director with a single executable bash command. This command should concatenate the physical Markdown file you just wrote straight into the active global retrospective document (e.g., `RETRO_VS_REALITY_GAP_ANALYSIS.md`), and then safely purge the JSON artifacts to reset the sandbox for the next session. (e.g., `cat docs/retrospectives/YYYY-MM-DD_architect_wrapup.md >> docs/retrospectives/YOUR_ACTIVE_RETRO.md && rm artifacts/*_handoff.json`).