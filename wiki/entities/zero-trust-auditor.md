---
title: "Zero-Trust Auditor"
date: 2026-06-02
category: entity
tags:
  - agent
  - security
  - auditor
  - zero-trust
  - promotion
sources:
  - "[[docs/retrospectives/2026-04-23_hvr_agentic_os_meta_retrospective.md]]"
  - "[[docs/retrospectives/2026-04-24_era_5_head_to_head_conclusion.md]]"
last_ingested: 2026-06-02
---

# Zero-Trust Auditor

The Auditor is the final gate in the [[agentic-os]] deployment pipeline. It structurally validates code quality, verifies cryptographic signatures, and promotes the `.staging/` payload into the root workspace — or rejects it back to the [[director-agent]] for remediation.

## Responsibilities

1. **Cyclomatic Complexity Verification**: Measures McCabe complexity of all generated code. Rejects anything with a per-function score > 5.
2. **AST Validation**: Runs Python AST parsing to catch syntax errors and structural defects.
3. **HMAC Signature Verification**: Validates the `.qa_signature` file written by the [[qa-engineer-agent]] via `transfer_to_development_workflow`. This cryptographic gate ensures code was physically verified by QA before promotion.
4. **Trivy CVE Scanning**: Executes vulnerability sweeps on dependencies (with `.trivyignore` for unexploitable VPC-isolated CVEs).
5. **Staging Promotion**: Calls `promote_staging_area()` to merge the validated sandbox contents into the root workspace via the `bin/dlp-firewall` binary.

## Textual Signals

- `[AUDIT PASSED]` — Terminates the `director_loop`, signaling successful deployment
- `[AUDIT FAILED]` — Triggers the [[director-agent]]'s macro-loop to re-route execution for remediation

## In-Situ Patching

The Auditor was refactored to support In-Situ patching ([docs/retrospectives/2026-04-23_iterative_macro_looping.md](../docs/retrospectives/2026-04-23_iterative_macro_looping.md)). Rather than wiping `.staging/` on metric failures (like complexity violations), it preserves the sandbox state and routes feedback back for targeted fixes.

## See Also

- [[staging-airlock]] — The sandbox it validates
- [[director-agent]] — The macro-loop that retries on audit failures
- [[dlp-proxy]] — The PHI redaction layer integrated into the promotion path
- [[zero-trust-interceptors]] — The signal routing infrastructure
