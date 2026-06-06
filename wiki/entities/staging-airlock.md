---
title: "Staging Airlock"
date: 2026-06-02
category: entity
tags:
  - security
  - sandbox
  - staging
  - zero-trust
sources:
  - "[[docs/retrospectives/2026-04-20_zero_trust_stabilization_and_telemetry.md]]"
  - "[[docs/retrospectives/2026-04-22_hierarchical_swarm_triumph.md]]"
last_ingested: 2026-06-02
---

# Staging Airlock

The `.staging/` directory is the physical air-gap environment where all agent-generated code executes before promotion to the root workspace. No agent can directly mutate the host file system — all writes are trapped inside this sandbox.

## Architecture

The staging airlock mirrors the root workspace structure. Agent tools like `write_workspace_file` automatically map relative paths into `.staging/`, creating a complete shadow copy. The airlock contains its own nested copies of `.agents/memory/` for ephemeral handoff ledgers.

## Security Mechanisms

### Fcntl Lock Throttling
The `.lock_mutex` file utilizes physical Unix/macOS kernel `fcntl` locking buffers. When parallel inference requests or API hallucination loops attempt to DDoS the system, the lock throws `BlockingIOError` states and imposes mandatory `time.sleep(5)` rate-limiting delays.

### Primed Cache
The `.primed` marker is set by `executor_mcp.py` to freeze subsequent workspace polling arrays and reduce continuous `shutil.copy2` overhead.

### Artifact Extraction
The extraction pipeline in `bin/run_kanban_benchmark.sh` uses `find -type f` and `cmp -s` differential comparison against the root workspace. Only files that physically differ or were exclusively created by the swarm are promoted.

## Promotion Flow

1. [[qa-engineer-agent]] writes `.qa_signature` HMAC token
2. [[zero-trust-auditor]] validates signature, complexity, and AST
3. Auditor calls `promote_staging_area()` which routes through `bin/dlp-firewall`
4. DLP firewall strips PHI before files reach the root workspace
5. Sandbox is reset for the next iteration

## See Also

- [[zero-trust-auditor]] — The gate that validates before promotion
- [[amnesia-sweep]] — The `git clean -fd` defense protocol
- [[dlp-proxy]] — PHI redaction in the promotion path
