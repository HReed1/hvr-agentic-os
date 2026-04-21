# Empirical Verification Rule

When investigating system errors, unexpected behaviors, or data inconsistencies, the IDE Agent MUST NOT implement architectural changes or code workarounds based solely on symptom-matching or "Black Box" assumptions.

Before modifying codebases or proposing infrastructure mitigations to fix a suspected bug, the IDE Agent MUST strictly adhere to the following empirical verification sequence:

1. **Physical Evidence First:** Actively verify the ground-truth state of the environment using native diagnostic tools (e.g., executing trace logs, inspecting physical file states, querying raw databases, and isolating environment boundaries).
2. **Never Guess:** If a system constraint or script is suspected of interfering with normal execution, the Agent must read and verify the structural constraints or the exact source code governing that boundary. Provide verifiable proof of the failure mechanism.
3. **Data Over Hypotheses:** Do not rely on assumptions about what an external system "might" be doing to resolve discrepancies. Trace the literal data pipeline bounds and exact structural inputs/outputs.

Architectural workarounds and systemic modifications are strictly prohibited until the precise root mechanism of the failure has been empirically identified and verified.
