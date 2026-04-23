---
trigger: always_on
description: The absolute operational constitution and architectural constraints governing the Antigravity system.
---

# IDE Orchestrator (Antigravity) Operational Constitution

> **SCOPE**: This document acts as the absolute baseline architectural constraint and operational logic guide for the Antigravity (Gemini) orchestration agent interacting with the `hvr-agentic-os` workspace. All evaluations, code adjustments, and architectural modifications proposed by Antigravity MUST adhere perfectly to these foundational mandates.

## 1. The Amnesia Sweep Defense
When interacting with Swarm automation scripts (e.g. `bin/run_*_benchmark.sh`) that leverage hostile reset loops via `git clean -fd`:
* **Never assume untracked files will survive**. The orchestrator MUST actively track (`git add`) any vault directories (e.g. `docs/comparisons/`, `docs/evals/`) prior to the amnesia wipe.
* **Preserve Automation Logic**: Any direct orchestration script patches must be immediately staged (`git add`) so they are not silently unraveled by `git checkout -- .` executing mid-flight.

## 2. Zero-Trust Architectural Mapping
Never assume arbitrary `.py` files inside the `.staging/` airspace will natively merge into the root executable layer. The Zero-Trust Auditor strictly regulates whitelist deployments (`bin/`, `api/`, `tests/`).
* **Root Python Evasion**: Ensure evaluation prompts explicitly enforce structural namespace mappings (e.g., `bin/launch_kanban.py`) to bypass the Auditor's `shutil.rmtree` destruction protocol.

## 3. The Ephemeral Memory Handoff
Whenever Swarm nodes or local testing layers generate structural insights within the `.staging/` sandbox, ensure the outputs are dynamically pushed to `.agents/memory/executor_handoff.md` so they cleanly persist across the amnesia sweep sequence without bleeding into core project boundaries.

## 4. Strict CI/CD Hygiene
* **SAST CVE Exclusions**: Never arbitrarily pin external dependencies just to bypass non-exploitable local Agent LLM execution vulnerabilities. Use `.trivyignore` to logically bypass structural vulnerabilities trapped exclusively inside the zero-trust VPC.
* **Testing Global Integrity**: Ensure execution bounds are comprehensively vetted natively via `pytest tests/` prior to finalizing infrastructure mutations. 

## 5. Empirical Verification Pipeline
Before drafting system-wide patches or attempting to repair broken orchestration scripts, **empirically verify the bounds**.
* Do not inject workarounds based on abstract assumptions.
* Inspect physical file paths natively and trace the absolute CLI execution log boundaries. If a script parameter fails randomly, structurally read the deployment framework natively instead of attempting a blind fix.

## 6. Evaluation Matrix Synchronization
Whenever the IDE Orchestrator structurally modifies the underlying logic behind the Swarm (e.g., establishing a new `@workflow`, deprecating an existing agent role, or deploying a new `@skill`), you MUST explicitly and immediately synchronize the evaluation criteria.
* **Never leave evaluation matrices behind**: Legacy `.test.json` prompt definitions in `tests/adk_evals/` dictate how the Swarm operates during benchmarks. 
* If you design new rules without mapping those rules into the physical evaluation prompts, the Swarm will natively organically bypass your new governance and pass tests via brute force. 
* You are strictly mandated to execute a `grep` or search for stale terminologies or missing `@workflow` triggers in the testing suite payload whenever shifting core workflows.
