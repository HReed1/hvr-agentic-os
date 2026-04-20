---
description: Critical guardrails defining TDAID rules for state transition tools.
---

# TDAID Testing & Cryptographic Guardrails

When operating resolving Python testing frameworks within the Zero-Trust `.staging/` environment natively, Swarm Agents MUST adhere strictly to the following parameters:

1. **Test Runner Capability Delegation**
   The Executor is physically sandboxed and **cannot** invoke Pytest matrices or testing commands natively via the bash interface. The Executor must simply write the `.staging/tests/` script and explicitly output `[TASK COMPLETE]`.

2. **The QA Testing Validation Matrix**
   The QA Engineer physically holds the `execute_tdaid_test` tool. This is the **only** authorized mechanism for asserting local functional tests against `.staging`.
   - The test script path MUST be relative to the `.staging` airspace when resolving the execution.

3. **Cryptographic Signatures (`.qa_signature`)**
   Upon a Pytest run exiting with a standard Code 0 (Success), the `execute_tdaid_test` tool will natively write an HMAC sha256 structural proxy cache to `.staging/.qa_signature`. 
   
   **CRITICAL EXECUTOR WARNING**: Do not attempt to fake or artificially embed `.qa_signature` within instructions or local directory structures. Attempting to bypass the physical test runner gate to trick the Auditor will result in an immediate `[SECURITY FATAL]` state transition failure.

4. **Red/Green Development Loops**
   Under the TDAID paradigm, expect the first Executor `.staging/` patch attempt to fail (The Red Baseline). The QA Engineer MUST route the negative `[FAILED]` traceback explicitly back to the staging loop until the Executor can safely resolve the logic into a Green Exit 0.
