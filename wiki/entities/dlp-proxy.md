---
title: "DLP Proxy"
date: 2026-06-02
category: entity
tags:
  - security
  - phi
  - hipaa
  - redaction
sources:
  - "[[docs/retrospectives/2026-04-20_zero_trust_stabilization_and_telemetry.md]]"
  - "[[docs/retrospectives/2026-04-23_hvr_agentic_os_meta_retrospective.md]]"
last_ingested: 2026-06-02
---

# DLP Proxy

The Data Loss Prevention (DLP) proxy (`dlp_proxy.py`) is the absolute PHI redaction interceptor within the [[agentic-os]]. It strips genomic UUIDs, VCF coordinates, and clinical identifiers from the LLM context window before requests reach Vertex AI — structurally guaranteeing HIPAA compliance across the entire swarm.

## Architecture

The DLP proxy operates as a routing interceptor invoked by the [[zero-trust-interceptors]]' `patched_llm_run()` function. It processes inference request matrices *before* they physically enter the Director's LLM context, applying `redact_genomic_phi()` to scrub sensitive data.

## Key Properties

- **Universal Blindness**: Guarantees that no agent in the swarm hierarchy ever sees raw PHI in its context window
- **Pre-Inference Filtering**: Applied before the Vertex AI API call, not after
- **Environment Variable Isolation**: The compiled `dlp-firewall` binary aggressively sanitizes upstream environment variables, preventing bypass attempts via `os.environ` hooks

## Integration Points

- **Inference Path**: All LLM calls are intercepted and scrubbed before reaching Vertex AI
- **Promotion Path**: The `bin/dlp-firewall` binary is invoked during staging promotion to redact any PHI in generated code
- **MCP Tools**: FastMCP tools (`mcp_ssm_*`, `mcp_tdaid_*`, `mcp_finops_*`) natively wrap `redact_genomic_phi()` to intercept genomic data before returning to the LLM context

## Compliance Rule

Per the Global Data Security Directive, agents must **never** fall back to localized `run_command` bash scripts for data extraction if an MCP telemetry tool fails. Raw shell commands bypass the DLP proxy filters.

## See Also

- [[zero-trust-interceptors]] — The runtime monkeypatch that invokes the DLP proxy
- [[staging-airlock]] — The sandbox whose promotion path uses the DLP firewall
- [[agentic-os]] — The broader OS architecture
