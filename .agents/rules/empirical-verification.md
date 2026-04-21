---
trigger: always_on
description: Mandatory empirical verification protocol for the IDE Agent to prevent assumption-based architectural workarounds.
---

# Empirical Verification Rule

> [!IMPORTANT]
> **Scoping**: This rule applies STRICTLY to the Antigravity IDE Agent (the outer orchestrating AI). It governs the IDE's analytical behavior when investigating anomalies.

When investigating system errors, unexpected behaviors, or data inconsistencies, the IDE Agent MUST NOT implement architectural changes or code workarounds based solely on symptom-matching or "Black Box" assumptions.

Before modifying codebases or proposing infrastructure mitigations to fix a suspected bug, the IDE Agent MUST strictly adhere to the following universal empirical verification sequence:

1. **Physical Evidence First**: Actively verify the ground-truth state of the environment using native diagnostic tools. This includes executing trace logs, inspecting physical file states, and querying actual databases rather than relying on session memory.
2. **Never Guess System Bounds**: If a system constraint, script, or environment boundary (e.g., a firewall, sandbox, or permission gate) is suspected of interfering with normal execution, the Agent must read and verify the structural constraints or the exact source code governing that boundary. Provide verifiable proof of the failure mechanism.
3. **Trace the Literal Data Pipeline**: Do not rely on assumptions about what an external system "might" be doing. Trace the literal data pipeline bounds and exact structural inputs/outputs to identify the precise point of failure.

Architectural workarounds and systemic modifications are strictly prohibited until the precise root mechanism of the failure has been empirically identified and verified through direct inspection.
