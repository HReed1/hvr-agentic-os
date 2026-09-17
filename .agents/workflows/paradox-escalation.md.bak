---
description: Natively halt Execution Loops and explicitly hand control back to the IDE Director when encountering unresolvable tooling paradoxes.
---

# Paradox Escalation Workflow

**Trigger:** You must execute this protocol IMMEDIATELY if you realize that your directive contradicts the physical environment, or if you are locked out of executing a critical tool (e.g. `execute_tdaid_test`) due to hard-coded environmental sandbox bounds (like `.staging/` missing).

## Execution Steps

1. **Halt Operations**: Do not attempt to bypass the sandbox, write dummy files, or invent log tracebacks. 
2. **Identify the Paradox**: Document exactly *why* you cannot proceed (e.g., "The Director ordered me to patch a namespace that physically does not exist," or "I received `[QA REJECTED]` twice for the same unresolvable issue").
3. **Escalate**: Invoke the `escalate_to_director` tool. 

   - If you are the **Executor or QA Engineer**: You must natively invoke `escalate_to_director(reason)`.
   - If you are the **Director**: Re-evaluate the directive you originally constructed. Read the traceback logs natively, repair the logical discrepancy or missing dependencies in your instructions, and explicitly draft a new iteration. If the paradox is external or terminal, you MUST explicitly escalate textually to the Human Operator.
