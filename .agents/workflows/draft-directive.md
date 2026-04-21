---
description: Synthesize a problem, enforce constraints, and generate a strictly formatted command prompt for the Swarm Hierarchy. Read-Only execution.
---

# Draft Implementation Directive

**Purpose:** Used by the orchestrating persona to synthesize engineering intent into a highly constrained implementation command for its immediate subordinate.

## Workflow Execution Steps

1. **Holistic Assessment**: Parse the Lead Engineer's or global framework's feature request, bug report, or design scope.
2. **Context Intersection**: Cross-reference the proposed solution against root-level boundaries (e.g., `AGENTS.md`, `fastapi-zero-trust.md`) to ensure Zero-Trust, Glassmorphism, and FinOps axioms are not violated. DO NOT use IDE-specific `.agents/rules` definitions if generating for a Headless persona.
3. **Polymorphic Output Generation**: Generate the final prompt, structuring the target payload based on your runtime identity:
   - *If executed by the IDE Director:* Output must be addressed to `**@director**` (the CLI Swarm Conductor), instructing it to triage parsing and dispatch.
   - *If executed by the CLI Architect:* Output must be addressed to `**@executor**`, strictly dictating the tactical boundaries.
4. **TDAID Injection Checkpoint**: Your finalized prompt MUST contain explicit instructions regarding the Executor's Pytest boundary testing logic. Append the following explicitly to the Execution Steps of the generated output:
   * *"Create an offline isolated TDAID Python test asserting the required mutation (Red/Green schema) targeting your modifications. You are the author ONLY. You do NOT have the capability to execute tests. Do NOT hallucinate testing tools or bash runners. The QA Engineer will physically use `execute_tdaid_test` to validate your work after you handoff. Once you have written the `.staging` codebase, output [TASK COMPLETE]."*
5. **Tool/Workflow Injection**: Structure execution commands dynamically by instructing the subagent to query its localized internal tools/skills before execution. Do not rigidly force IDE slash-commands (like `/tactical-override`) if instructing the Headless CLI Executor, unless verifying they possess that identical skill internally.
6. **Export**: Write the strictly formatted markdown directive BOTH as a physical Markdown file saved to the repository (e.g. `docs/retrospectives/YYYY-MM-DD_[name].md`) conforming to standard documentation formatting, AND as a mirrored native Antigravity Artifact (`write_to_file` using `IsArtifact: true`) straight to the UI. DO NOT attempt to mutate literal source code.