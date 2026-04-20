---
name: finops-s3-sanitation
description: Deploys targeted AWS S3 bucket garbage collection protocols. Use this to safely sweep and remove orphaned Nextflow `-resume` caching payloads while respecting FinOps blast-radius guardrails.
---

# FinOps S3 Sanitation Array

When AWS Batch I/O scaling limits are breached, massive residual artifacts persist within the S3 cloud-bucket environments (`[work/a-f0-9...]`). 

## When to use this skill
- When requested to flush dead pipeline execution directories. 
- When evaluating FinOps cost overruns due to S3 byte volume.

## How to use it
You must execute the encapsulated JSON payload: `mcp_finops-infrastructure-oracle_trigger_s3_sanitation`.
1. **The Assessment Phase**: You must first perform a structural byte calculation. Run `mcp_finops-infrastructure-oracle_trigger_s3_sanitation` with `dry_run: true`. This natively triggers the `assess_s3_sanitation_blast_radius` tracking mechanics.
2. **Halt and Report**: Print the dry-run byte volume and total object count directly to the user in your context response.
3. **The Air-Gap Firewall**: You are **EXPLICITLY FORBIDDEN** from invoking `mcp_finops-infrastructure-oracle_trigger_s3_sanitation` with `dry_run: false` blindly. You MUST evaluate the byte size and actively wait for the Director to give explicit approval to proceed with physical bucket dropping.
4. **Execution Protocol**: If the user desires to execute the deletion, you must run `mcp_finops-infrastructure-oracle_trigger_s3_sanitation` with `dry_run: false`. This natively spans across the AWS infrastructure and physically deletes S3 buckets.
