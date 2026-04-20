---
description: The Director's protocol for autonomously generating and injecting highly-contextual weekly documentation summaries.
---

# Weekly Documentation Synthesis Pipeline

**Trigger Constraint:** Execute this pipeline whenever the user requests the generation or refactoring of a "weekly summary," "weekly description," or whenever structural documentation updates leave the `docs/retrospectives/2026-04-15_weekly_evolution_review.md` file with out-of-date or generic placeholders.

**Purpose:** To automate the extraction of dense technical context spanning 10-40+ documents and safely compress that data into an accurate, high-fidelity weekly narrative.

## Workflow Execution Steps

1. **Index Verification:** Before synthesizing any context, run `./utils/build_project_llms_txt.py` to ensure the global documentation index (`llms-full.txt`) is perfectly up to date with the latest directory structures and `README.md` metadata.
2. **Context Extraction:** Parse `docs/retrospectives/2026-04-15_weekly_evolution_review.md` to identify the specific target week and extract the exact filenames and commit headers listed under that block. Cross-reference those filenames against the fresh `llms-full.txt` map to securely extract context payloads.
3. **Narrative Synthesis:** Draft a highly dense, 3-7 sentence paragraph specifically isolating the architectural milestones, core FinOps/Zero-Trust integrations, and pipeline challenges encountered during that week. 
    * *Assertion Constraint:* If the week contains pivotal shifts (like the ADK refactor, Agentic Evals, or Auth0 interceptions), these *must* clearly anchor the paragraph.
4. **Structural Injection:** Programmatically read the `docs/retrospectives/2026-04-15_weekly_evolution_review.md` file natively and substitute the generic placeholder block safely without disrupting the existing markdown reference links.
5. **Validation:** Analyze a `git diff` chunk of the file boundary natively or capture local file views around the injection hook to assert perfect markdown structural preservation.
