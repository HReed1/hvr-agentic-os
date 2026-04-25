---
trigger: always_on
description: Guardrails for evaluating and vaulting architectural payloads during cyclical testing phases (Amnesia Sweeps).
---

# Execution Loop Amnesia Defense

When writing bash automation scripts or handling continuous evaluations that rely on isolated testing sandboxes (like `.staging/`), Swarm Agents and the Director MUST strictly adhere to the following Amnesia Defense protocol.

1. **Amnesia Sweep Vectors (`git clean -fd`)**
   Any architectural loop utilizing `git clean -fd` to purge state between runs will aggressively vaporize ALL untracked directories system-wide. This includes newly generated artifact directories (`docs/comparisons/`, `docs/evals/`, etc.). 
   
2. **Pre-Emptive Artifact Vaulting**
   If an evaluation framework requires capturing metrics or generated code into an output directory *prior* to a `git clean -fd` amnesia sweep, you MUST explicitly pre-empt the destruction by indexing the vault directory:
   - *Example Fix:* `git add "$ARTIFACT_DIR"` MUST be executed immediately before `git clean` to safely shift the payload out of untracked status.

3. **Untracked Script Disintegration (`git checkout -- .`)**
   Bash runner scripts themselves are subject to amnesia sweeps if they are mutated and left uncommitted. Any live modifications to orchestration scripts (like `run_benchmark.sh`) must be followed precisely by a `git add` execution to prevent `git checkout -- .` from rolling back the orchestrator mid-flight.

4. **Zero-Trust Promotion Boundaries**
   Never assume generic root-level Python scripts engineered inside the evaluation sandbox will natively migrate to the root project airspace. The Zero-Trust Auditor enforces strict folder mapping. All execution payloads designed to survive promotion should map cleanly to inherently trusted sub-directories (e.g. `bin/` or `api/`).
