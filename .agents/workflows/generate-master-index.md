---
description: Natively generates the HVR Knowledge Graph master_index.json mapping architectural milestones and eras from llms.txt and weekly retrospectives.
---

# Master Index Generation Pipeline

**Trigger Constraint:** Execute this pipeline whenever the user requests the creation, reconstruction, or update of the `master_index.json` Knowledge Graph.

**Purpose:** To consume chronological project logs (`llms.txt` and `weekly_evolution_review.md`) and securely transition them into a structured JSON schema mapping Eras, Pivots, Commits, Philosophical goals, and Simulation Scenarios.

## Workflow Execution Steps

1. **Backup Phase:** Before writing anything, the IDE MUST back up the current `/Users/harrisonreed/Projects/ngs-variant-validator/master_index.json` natively. Move a copy to `docs/blog/legacy/master_index_YYYY_MM_DD.json`.
2. **Context Intake:** Utilize `view_file` to read the fully built `llms.txt` mapping and the `docs/retrospectives/2026-04-15_weekly_evolution_review.md`.
3. **Data Structuring:** Synthesize the temporal layout into the following explicit JSON schema constraint (HVR Knowledge Graph):
    * `era_id`, `name`, `date_range`
    * `pivots`: Array of objects containing:
        * `title`: A human-readable milestone block.
        * `commit`: A verifiable 7-character Git hash corresponding to reality.
        * `date`: The timeline marker.
        * `philosophical_pivot`: The underlying architectural narrative.
        * `simulation_scenario`: Object containing `challenge_type` and `reader_task`.
4. **Execution:** Write the payload out strictly to `master_index.json`. Do not truncate; output the entire graph.
5. **Validation:** Execute a fast `cat master_index.json | jq .` via `run_command` natively to assert perfect programmatic syntax and prevent UI crashes downstream.
