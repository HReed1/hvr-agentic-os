---
description: The systemic decision-tree and local diagnostic tool sequence for evaluating dead AWS Batch orchestrated pipeline failures.
---

# AWS Batch Triage Protocol

**Purpose:** When encountering an "Essential container in task exited" MCP error, follow this sequence to avoid useless speculation and extract physical data via Zero-Trust SSM tunnels.

## Workflow Execution Steps

### 1. Identify the Exit Code Vector
* **Exit 137 / Exit 140 (OOM)**: In this context, these exit codes indicate the Linux Out-Of-Memory (OOM) Killer destructively terminated the container because its memory footprint (e.g., DeepSomatic shards) forcibly exceeded the allocated EC2 instance boundary. Cross-reference `main.nf` RAM declarations against native EC2 capacities (`infrastructure/aws/main.tf`). Utilize the associated MCP tools (e.g. `mcp_aws-batch-diagnostics_get_live_container_ram`) to track profiles. **CRITICAL GUARDRAIL:** You may ONLY execute live telemetry tools against active `RUNNING` jobs. Do NOT attempt to execute SSM telemetry against `FAILED` jobs.
* **Exit 28 (ENOSPC)**: Identify EBS physical blockade. Check the block device allocations in the primary `aws_launch_template`. Run the `mcp_aws-batch-diagnostics_get_live_container_disk` tool natively to monitor node partitioning loops.
* **Exit 127 (Command Not Found)**: Container drift. Read `docs/gemini/CONTEXT_CONTAINER_REGISTRY.md` to verify if the Nextflow target process has been dynamically mapped to a Docker repository that lacks the requisite operational binaries.

### 2. Verify Output Trajectory
Ensure all tools implemented natively during debugging are "Read-Only Observability". Do not manipulate, delete, or shell into actively staged cloud resources via write commands without explicit Director mandates.
