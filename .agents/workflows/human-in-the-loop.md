---
description: An explicit Human-in-the-Loop workflow requiring the Director to map permission gates, and the Auditor to physically solicit manual human approval using the CLI prior to integrating sandbox airlocks.
---

# Human-In-The-Loop Approval

**Purpose:** This workflow guarantees absolute zero-trust verification of highly sensitive algorithmic operations. By mandating explicit human oversight directly via the CLI, the Swarm structurally prevents unilateral modification to high-liability DAG orchestrations or Infrastructure as Code state files.

## Workflow Execution Steps

1. **Director Orchestration**: The Director natively interprets that the user's objective requires a "Human in the Loop". The Director MUST explicitly encode this requirement into its standard directive explicitly so the downstream Auditor understands it must fetch authorization at the end of the line. (e.g., `"[@auditor]: You must fetch human approval before deploying this payload."`)
2. **Standard Staging**: The Executor and QA Engineer author and validate the structural files exactly as instructed inside the `.staging/` airspace, securely triggering the `approve_staging_qa` tool.
3. **Auditor Interception**: The Auditor assesses the `.staging/` airspace natively using the `AUDITOR_MCP_PATH` tools to establish its baseline safety constraints.
4. **Tool Escalation**: Upon verifying the changes are safe, because the Director explicitly broadcasted a Human-In-The-Loop requirement, the Auditor MUST natively execute the `get_user_choice` tool. This physically halts execution and prompts the CLI user with custom deterministic query strings (e.g., `["Approve Deployment", "Reject changes", "Teardown staging"]`).
5. **Disposition**:
   - If the user selects "Approve Deployment", the Auditor invokes `promote_staging_area` and outputs `[AUDIT PASSED]`.
   - If the user selects "Reject changes" or "Teardown staging", the Auditor invoked `teardown_staging_area` and gracefully outputs `[AUDIT FAILED]`.
