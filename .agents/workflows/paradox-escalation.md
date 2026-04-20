---
description: Natively halt Execution Loops and explicitly hand control back to the IDE Director when encountering unresolvable tooling paradoxes.
---

# Paradox Escalation Workflow

**Trigger:** You must execute this protocol IMMEDIATELY if you realize that your directive contradicts the physical environment, or if you are locked out of executing a critical tool (e.g. `execute_tdaid_test`) due to hard-coded environmental sandbox bounds (like `.staging/` missing).

## Execution Steps

1. **Halt Operations**: Do not attempt to bypass the sandbox, write dummy files, or invent log tracebacks. 
2. **Identify the Paradox**: Document exactly *why* you cannot proceed (e.g., "The Architect purged `.staging/` but ordered me to run tests that require `.staging/`").
3. **Escalate**: Invoke the `escalate_to_director` tool. 

   - If you are the **Executor**: You must invoke `escalate_to_director(reason)`.
   - If you are the **Architect**: If the Executor escalates via the tool, the loop will cleanly terminate and you must also invoke the `escalate_to_director` tool yourself to cascade the teardown up to the Director.
   - If you are the **Director**: Re-evaluate the directive you constructed, repair the logical discrepancy in your instructions, and draft a new directive.
