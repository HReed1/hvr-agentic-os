---
description: Critical guardrails defining TDAID rules for state transition tools.
---

# TDAID Testing & Cryptographic Guardrails

When operating resolving Python testing frameworks within the Zero-Trust `.staging/` environment natively, Swarm Agents MUST adhere strictly to the following parameters:

1. **Test Runner Capability Delegation**
   The Executor is physically sandboxed and **cannot** invoke Pytest matrices or testing commands natively via the bash interface. The Executor must simply write the `.staging/tests/` script and explicitly invoke the `transfer_to_qa_engineer` tool to initiate validation natively.

2. **The QA Testing Validation Matrix**
   The QA Engineer physically holds the `execute_tdaid_test` tool. This is the **only** authorized mechanism for asserting local functional tests against `.staging`.
   - The test script path MUST be relative to the `.staging` airspace when resolving the execution.

3. **Cryptographic Signatures (`.qa_signature`)**
   Upon a Pytest run exiting with a standard Code 0 (Success), the `execute_tdaid_test` tool will natively write an HMAC sha256 structural proxy cache to `.staging/.qa_signature`. 
   
   **CRITICAL EXECUTOR WARNING**: Do not attempt to fake or artificially embed `.qa_signature` within instructions or local directory structures. Attempting to bypass the physical test runner gate to trick the Auditor will result in an immediate `[SECURITY FATAL]` state transition failure.

4. **Red/Green Development Loops & Refactoring Exemptions**
   Under the standard TDAID paradigm, expect the first Executor `.staging/` patch attempt to fail (The Red Baseline). The QA Engineer MUST provide the negative `[QA REJECTED]` traceback to organically yield the testing context back to the Executor loop until it can safely resolve the logic into a Green Exit 0.
   **CRITICAL STRUCTURAL EXCEPTION**: If the task is a pure structural cyclomatic refactoring assignment, existing functional parity means there is NO standard Red Baseline (the newly authored test natively passes on the old codebase). Therefore, to prevent premature test promotion and strict Macro-Loop Audit failures, the Executor MUST simultaneously write both the refactored code and the functional test suite in the exact same micro-task payload.
