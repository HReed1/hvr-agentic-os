---
description: The Emergency Brake protocol. Run this script natively before executing significant architectural Nextflow DAG or Terraform variable changes.
---

# Blast Radius Assessment

**Purpose**: Invoked by the AI Execution layer when proposed modifications intersect with critical system infrastructure (DAG structures, container capacities, Terraform state boundaries). Validates changes out-of-band to prevent "Ghost Pathing" degradations.

## Workflow Execution Steps

1. **Evaluate DAG Propagations**: Given an execution block change (e.g., injecting a `--split-3` SRA extraction loop), physically trace the output schema (tuple dimensions) recursively downstream into `main.nf` to visualize channel starvations or type-cast collisions. 
2. **Verify Hardware Limits**: If `nextflow.config` limits (cpus, request_memory) are inflated, read `infrastructure/aws/main.tf` to guarantee the associated Launch Template instances can support the load without triggering automated scheduler crush.
3. **Denial Strategy**: If systemic inconsistencies are spotted, immediately abort standard `.md` plan generation and reject the prompt via the prompt window. Output the generated "Ghost Pathing Violation" report for the Lead Engineer to re-assess the directive payload.
