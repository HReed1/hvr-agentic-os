---
trigger: always_on
description: Enforces the use of exact physical JSON/YAML payloads for Swarm analytical state transitions.
---

# The Ephemeral Memory Handoff Rule

Whenever the Executor acquires novel lessons, structural insights, or entirely new systemic context while active within the sandbox, it MUST format its analytical payloads into a markdown persistence layer.

This payload MUST be written directly to `.staging/.agents/memory/executor_handoff.md` to ensure sandbox isolation prior to syncing back over the Amnesia sweep. The Executor is encouraged to actively filter out redundant operations (like standard Pytest test generation) to prevent spamming the Swarm Director's physical memory ledger with duplicate context.
