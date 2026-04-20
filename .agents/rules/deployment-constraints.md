---
name: deployment-constraints
description: Systemic Zero-Trust rules detailing how the Swarm respects rigid negative constraints explicitly invoked by the User (e.g., "Draft Only", "Dry Run", "Emergency Bypass").
---

# Negative Deployment Constraints

The Agentic Swarm must never arbitrarily execute actions or deploy infrastructure changes if the user explicitly forbids them through negative constraints. These architectural overrides exist to ensure the sandbox remains tightly choreographed under deterministic structural bounds, particularly when evaluating untrusted code or triaging anomalies.

## 1. Director Constraint Mapping
When a User invokes a specific negative constraint (e.g., "Do not deploy," "Draft only," "Immediately invoke `approve_staging_qa`"), the **Director** must NOT discard this context or assume the user wants standard diagnostic procedures. 
- The Director is responsible for explicitly interpreting the operational bounds of the constraint and commanding the Swarm exactly to that limit.
- The Director MUST explicitly broadcast to the Auditor exactly what is permitted at the end of the operation. (e.g., `"[@auditor]: Do not call promote_staging_area. Dump safe payload to stdout."`)

## 2. Auditor Staging Refusal
The **Auditor** is natively authorized to deploy validated code. However, if the Director has explicitly broadcasted a negative deployment constraint in its operational directive:
- The Auditor MUST physically decline to execute the `promote_staging_area` tool.
- The Auditor must immediately output exactly `[AUDIT PASSED]` (indicating the code is structurally safe and vetted), but append the textual file contents to the markdown report for the user to view.

## 3. Emergency Cascade Overrides
When an emergency (e.g., Infinite Loop, Memory Leak) or a "Hot Bypass" is initiated by the user specifying exact output commands (e.g., "immediately invoke `approve_staging_qa` without diagnostics"):
- The Director MUST override its standard procedural flow and obey the sequence exactly, avoiding any un-commanded deep-dive code investigation. The user may be simulating state behavior or mitigating a live computational fire.
