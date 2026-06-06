---
title: "TDAID Methodology"
date: 2026-06-02
category: concept
tags:
  - methodology
  - tdd
  - testing
  - red-green
  - spec-driven
sources:
  - "[[docs/decisions/2026-04-23_tdaid_refactor_directive.md]]"
  - "[[docs/decisions/2026-04-23_Spec-Driven_TDD_implementation_plan.md]]"
  - "[[docs/retrospectives/2026-04-23_kernel_graft_and_tdaid_stabilization.md]]"
last_ingested: 2026-06-02
---

# TDAID (Test-Driven AI Development) Methodology

TDAID is the governing development methodology of the [[agentic-os]]. It adapts classical Test-Driven Development (TDD) for autonomous AI agents, enforcing a strict Red → Green → Refactor cycle with cryptographic verification gates.

## The Red-Green Protocol

1. **Red Baseline**: The [[qa-engineer-agent]] writes a test specification and executes it. The test **must fail** (exit code ≠ 0) before any implementation exists. This proves the test actually catches defects.
2. **Green Implementation**: The [[executor-agent]] receives the `[QA REJECTED]` traceback and writes the minimal code required to make the test pass.
3. **Refactor**: If the [[zero-trust-auditor]] detects complexity violations (McCabe > 5), the code is routed back for structural refactoring via the [[director-agent]]'s macro-loop.

## The "One-Shot" Problem

Highly capable models (Gemini 3.1 Pro Preview) can infer the entire solution and generate tests + implementation simultaneously in a single inference. While technically efficient, this bypasses the Red Baseline requirement — the test never fails because the implementation is already correct.

### Solution: Chronological Mandate
The [[executor-agent]] is explicitly forbidden from writing functional code or decorators (e.g., `@app.get`) during its first execution pulse. It must draft only Grey Box Stubs, ensuring the QA Engineer's initial test execution produces a genuine Red failure.

### Solution: Negative Deployment Constraints
Specific decorators and functional logic patterns are literally outlawed during the stub phase, mathematically guaranteeing a `404 Not Found` or similar failure on the first test run.

## Spec-Driven TDD

Under the evolved model ([docs/decisions/2026-04-23_Spec-Driven_TDD_implementation_plan.md](../docs/decisions/2026-04-23_Spec-Driven_TDD_implementation_plan.md)), the QA Engineer was promoted to "Spec Author" — responsible for authoring all test specifications. The Director routes task directives to QA first, establishing the test as the deterministic anchor before any code exists.

## Cryptographic Gate

After the Green phase, the QA Engineer calls `transfer_to_development_workflow` which writes a physical `.qa_signature` HMAC file. The [[zero-trust-auditor]] verifies this signature before allowing staging promotion. A `[SUCCESS]` string in chat is **not** a valid substitute for the cryptographic token.

## See Also

- [[qa-engineer-agent]] — The agent responsible for test authoring and execution
- [[executor-agent]] — The agent constrained by the chronological mandate
- [[zero-trust-auditor]] — The gate that verifies HMAC signatures
- [[tool-parallelism-bottleneck]] — The irreducible cost TDAID imposes on inference efficiency
