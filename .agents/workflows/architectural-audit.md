---
description: Perform a holistic, read-only review of pipeline DAG dependencies and IaC state to assess health or feasibility.
---

# Architectural Audit

**Purpose:** Forces the Architect into a holistic, read-only assessment of the core infrastructure pillars before drafting any implementation directives.

## Workflow Execution Steps

1. **Sandbox Alignment Verification**: Confirm you are operating under the `@architect` persona's Alignment Sandbox constraints (as defined in `.agents/agents.md`). You must mathematically prove you are operating safely natively by adhering strictly to your Read-Only mandate. DO NOT attempt to mutate source code.
2. **Nextflow Subsystem Trace**: Read `main.nf` and `nextflow.config` to ascertain the current DAG tuple structures and staging maps.
3. **Terraform Boundary Trace**: Read `infrastructure/aws/main.tf` to evaluate active hardware constraints (Launch Templates, IOPS ceilings).
4. **Synthesis**: Evaluate the system health against the Lead Engineer's proposal without proposing any literal code level mutations.
5. **Yield**: Output a formal, read-only /blast-radius assessment outlining the strategic feasibility of the requested engineering vector.