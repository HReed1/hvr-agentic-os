---
title: "Amnesia Sweep Defense"
date: 2026-06-02
category: concept
tags:
  - defense
  - git
  - state-management
  - testing
sources:
  - "[[docs/retrospectives/2026-04-22_the_swarm_crucible_retrospective.md]]"
  - "[[docs/retrospectives/2026-04-22_hierarchical_swarm_triumph.md]]"
last_ingested: 2026-06-02
---

# Amnesia Sweep Defense

The Amnesia Sweep Defense is a protocol governing how the [[agentic-os]] protects critical artifacts from destruction by `git clean -fd` and `git checkout -- .` commands used between evaluation runs.

## The Threat

Evaluation bash scripts use `git clean -fd` to purge state between runs, creating isolated testing sandboxes. This aggressively vaporizes **all** untracked directories system-wide — including newly generated artifact directories (`docs/comparisons/`, `docs/evals/`), evaluation results, and even the orchestration scripts themselves if they've been modified.

## Defense Mechanisms

### 1. Pre-Emptive Artifact Vaulting
If an evaluation framework captures metrics or generated code into an output directory prior to a `git clean -fd` sweep, the directory must be pre-emptively staged:
```bash
git add "$ARTIFACT_DIR"   # Shift out of untracked status before clean
```

### 2. Script Self-Protection
Bash runner scripts themselves are subject to amnesia sweeps if modified and left uncommitted. Any live modifications to orchestration scripts must be immediately followed by `git add` to prevent `git checkout -- .` from rolling back the orchestrator mid-flight.

### 3. Ephemeral Memory Handoff
Novel lessons and structural insights acquired during sandbox execution are written to `.staging/.agents/memory/executor_handoff.md` — inside the sandbox boundary — to ensure they survive the amnesia sweep via the normal staging promotion flow.

### 4. Zero-Trust Promotion Boundaries
Scripts engineered inside the evaluation sandbox cannot be assumed to survive to the root workspace. All execution payloads designed to survive promotion must map to inherently trusted sub-directories (`bin/`, `api/`).

## See Also

- [[staging-airlock]] — The sandbox boundary that provides isolation
- [[evaluation-framework]] — The system that triggers amnesia sweeps
- [[drift-registry]] — Related governance mechanism for cross-file dependencies
