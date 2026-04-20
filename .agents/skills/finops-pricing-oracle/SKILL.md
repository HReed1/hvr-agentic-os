---
name: finops-pricing-oracle
description: Read-only tool to pull static/live AWS Spot and On-Demand pricing JSONs to calculate the exact financial Blast Radius of scaling operations.
---

# FinOps Pricing Oracle

**Purpose:** Calculate the exact financial Blast Radius of a proposed Nextflow scaling execution.

## When to use this skill
* When proposing changes that will geometrically increase `maxForks` or AWS Batch compute queue mappings.
* When calculating projected EC2 Spot arbitrage overhead for new pipelines.
* When auditing Nextflow Config queue assignments to ensure CPU-bound tools are not improperly driving up costs on GPU nodes.

## How to use it
* Execute `python3 .agents/skills/finops-pricing-oracle/oracle.py`.
* This tool is strictly **READ-ONLY**. It fetches static or live metadata regarding instance markets and outputs JSON dictionaries representing current thresholds.
* Cross-reference outputs natively against the `decimal` arithmetic protocol in `.agents/rules/finops-and-database.md`.
