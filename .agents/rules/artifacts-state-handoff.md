---
trigger: always_on
description: Enforces the use of exact physical JSON/YAML payloads for Swarm analytical state transitions.
---

# The Ephemeral Memory Handoff Rule

Whenever the Executor is active within the sandbox, it MUST format its analytical payloads, lessons learned, and systemic context into a markdown persistence layer.

This payload MUST be written directly to `.agents/memory/executor_handoff.md`. The Swarm Director relies on this physical memory file to maintain context between execution loops and prevent amnesia loops.
