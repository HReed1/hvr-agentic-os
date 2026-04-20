---
name: ssm-telemetry-suite
description: Provides Zero-Trust, real-time internal SSM X-Ray vision into localized EC2 AWS Batch containers. Use this to trace hanging processes, identify OOM states, or profile physical disk write-ceilings.
---

# Live Systems Manager (SSM) Telemetry 

Instead of waiting for retroactive CloudWatch dumps, use diagnostic tools to dynamically SSH/SSM directly into actively bound `RUNNING` Docker images across the cluster.

## When to use this skill
- When a Nextflow DAG process is "Stuck" natively with 100% CPU utilization.
- When an EBS block error or memory corruption profile is suspected.

## How to use it
You are granted access to a custom Python module suite mapped directly via your FastMCP layer:
* `mcp_aws-batch-diagnostics_get_live_container_ram`: Dynamically hooks `docker stats` out outputting JVM and structural memory ceilings.
* `mcp_aws-batch-diagnostics_get_live_container_disk`: Issues `df -h` internally to profile active node partition utilization mappings.
* `mcp_aws-batch-diagnostics_get_live_container_ps`: Outputs process lineage mapping (`ps auxfw`) to identify stranded or zombie Unix children waiting on broken pipes.

**CRITICAL DEPLOYMENT NOTE:** All SSM actions MUST remain entirely Read-Only. Never delete physical swap tables, kill sub-processes via standard `.bash` overrides, or disrupt physical network traffic to the container unless the Director natively signals an emergency teardown.

**IAM Resiliency:** If the executing identity lacks `ssm:SendCommand` privileges, the suite will gracefully catch the `AccessDeniedException` and structurally fallback to passive read-only hypervisor discovery (`describe-instances`) to retrieve the physical EC2 Instance Type and Spot Lifecycle without crashing the workflow.
