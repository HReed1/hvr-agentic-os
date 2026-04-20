---
trigger: always_on
description: Guardrails for dependencies, caches, and test CI/CD operations inside the sandbox.
---

# CI/CD & Tooling Hygiene Guardrails

When working with dependencies, caches, tests, and CI/CD operations, Swarm Agents MUST adhere to the following rules:

1. **State / Cache Tracking (`.gitignore`)**
   Agents must NEVER commit operational caches (e.g., `.terraform/`, `.compiled_ast_cache.nf`, `__pycache__/`, `.vite/deps/`). You must actively enforce their exclusion in `.gitignore` if generated during local testing to prevent systemic CI/CD pipeline collision loops.

2. **Dependency Hallucinations (`requirements.txt`)**
   Never append syntactical packaging flags (e.g., `[all]`) to Python dependencies without strict verification that the specific installed library version structurally provides that extra bundle. This triggers fatal PIP backtracking loops.

3. **Vulnerability Mitigation (`.trivyignore` / `--ignore-vuln`)**
   When bypassing localized Agent Simulation SDKs (e.g., `litellm`) that trigger generic SAST flags but remain physically unexploitable within the Zero-Trust VPC, DO NOT forcefully pin newer incompatible versions that shatter the overarching dependency tree. Instead, gracefully mute the specific unexploitable CVEs directly inside the GitHub Actions YAML runner or `.trivyignore`.

4. **Testing Mandate (Global Pytest Execution)**
   Prior to declaring `[EXECUTION APPROVED]`, merging changes, or triggering deployments, a full `pytest` run MUST be executed across the ENTIRE test suite (`pytest tests/`). The Director is STRICTLY FORBIDDEN from issuing orchestration directives that limit Executor testing verification to isolated/scoped subsets. Pull Requests and migrations are STRICTLY PROHIBITED if the global test matrix fails.
