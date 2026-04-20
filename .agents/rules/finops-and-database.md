---
description: Enforces mathematical FinOps arbitrage restrictions and global database rules for local metric scripts.
glob: "*.py"
---

# Global Python: FinOps & Database Guardrails

## FinOps Spot Arbitrage
* **STRICT FORBIDDEN PATTERN**: You are completely forbidden from using standard Python `float()` types for AWS Pricing arbitrage natively (e.g., `float(record['SpotPrice'])`).
* **The Fix**: You MUST invoke the standard library `decimal` module (`Decimal('0.0000')`) for all microbilling calculations to prevent catastrophic precision degradation when scaling across thousands of GPU hours.

## S3 Byte-Size Probing
* When querying AWS S3, extraction workflows must evaluate payload mass dynamically using `boto3.client('s3').head_object` (unsigned) to capture `ContentLength`. Massive (>20GB) payloads must be identified and hard-routed to On-Demand compute queues to prevent Spot interruption during massive synchronous block transfers.

## Python Telemetry String Matching
* **STRICT FORBIDDEN PATTERN**: You must NEVER use naive substring evaluation (e.g., `if "bam" in filename`) when parsing structural file outputs. This inherently collides with derivative index files like `.bam.bai` or `.bam.md5`.
* **The Fix**: Mandate strict `.endswith()` parsing or explicit ternary ordering for string isolation.

## PostgeSQL JSONB Telemetry
* When patching the `JSONB` telemetry logs directly, you must use native PostgreSQL jsonb concatenation: `UPDATE table SET metadata = COALESCE(metadata, '{}'::jsonb) || CAST(:m AS jsonb)`. DO NOT read, string-append, and overwrite data via Python objects.

## Local Execution
* If proposing bash terminal commands to run Python scripts, you MUST wrap them inside the active environment: `source venv/bin/activate && python script.py`.

## Architectural Database Probing
* When resolving Backend / FastAPI connection problems, you are mandated to use the `assert_postgres_telemetry` MCP tool natively to physically query the `frontend_runs` View. This asserts that Nextflow REST broadcasts are fully permeating the database layer down to the precise PostgreSQL tables without forcing you to negotiate raw Psql authentication syntax directly in the shell.
