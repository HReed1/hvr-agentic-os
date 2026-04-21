---
description: Critical guardrails defining how to properly construct and promote sandbox testing bounds.
---

# Staging Promotion & Sandboxing Protocol

All agents must adhere to the following file-isolation rules to ensure Zero-Trust environments remain untainted during testing and validation loops.

1. **Sandbox Confinement (`.staging/`)**
   The Executor's environment is dynamically chrooted. When evaluating structural tasks, use standard relative paths (e.g. `api/main.py`). The framework natively abstracts file mutations into the physical `.staging/` boundary. DO NOT forcibly prepend `.staging/` to arguments.

2. **AST Namespace Confinement**
   When authoring Pytest test scripts or dynamically loading modules within the `.staging/` airspace, **DO NOT** prepend `.staging` inside your Python `import` statements! 
   The testing framework dynamically forces the root `cwd` into the sandbox. 
   - **CORRECT:** `from api.batch_submitter import submit_genomic_job`
   - **FATAL ERROR:** `from .staging.api.batch_submitter import submit_genomic_job`

3. **Tooling Capability Confinement**
   - The Executor does **NOT** possess testing runner privileges or `promote_staging_area`. 
   - The QA Engineer does **NOT** possess deployment capabilities.
   - The **Auditor** is the sole cryptographic gatekeeper.

4. **Approval Loop Architecture**
   - The `Executor` and `QA Engineer` communicate back and forth iteratively within the standard development sandbox until the CI matrix natively runs green.
   - Once the QA engineer physically fires `mark_qa_passed`, the execution graph explicitly pushes the state boundary up to the `Auditor`.
   - The `Auditor` mathematically asserts the codebase structure and physically launches `promote_staging_area`.
