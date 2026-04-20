---
trigger: always_on
description: Mandatory guardrails for spot-market architectural limits and memory provisioning overheads.
---

# FinOps Integration (Spot Market Arbitrage) Guardrails

Agents must respect overarching financial operations (FinOps) architecture when provisioning resources or writing code:

1. **Database Relational Integrity & Memory Overhead**
   Enforce deep eager loading natively (e.g., using `selectinload` in SQLAlchemy). Doing so mechanically prevents `N+1` query degradation, severely reducing backend runtime taxation and unnecessary data ingress charges.

2. **AWS Batch Spot Reclamation Strategy**
   Compute provisioning inside Nextflow MUST natively include fallback mechanisms. Agents must orchestrate the routing so that whenever Spot reclaims occur, they instantly trigger a `task.attempt` that routes the retry directly to an On-Demand queue. This structurally completely prevents the pipeline from losing 60GB+ EBS state volumes when consecutive Spot interruptions occur.

3. **Hardware Queue Routing (CPU vs GPU)**
   Strictly route CPU-bound sequence algorithms (`ALIGN_BWA`, `ALIGN_BOWTIE2`, `ALIGN_MINIMAP2`) to generic CPU queues. Reserving expensive GPU instances (`somatic-gpu-queue`) for algorithms without CUDA architecture (everything EXCEPT `ALIGN_PARABRICKS` and `CALL_VARIANTS`) is a catastrophic FinOps violation.
