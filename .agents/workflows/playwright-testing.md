---
trigger: manual_or_director
description: Enforces Playwright best practices and zero-trust E2E testing scopes through the playwright-engineer skill.
---

# Playwright Testing E2E Workflow

This workflow MUST be executed whenever the Swarm is tasked with drafting end-to-end (E2E) UI test matrices against browser DOM interfaces. Due to the high complexity, strict mode paradoxes, and networking bounds inherent to Playwright AI orchestration, the Swarm MUST aggressively enforce formalized skillset definitions.

## 1. Skill Ingestion (MANDATORY)
The Director MUST structurally map the QA Engineer payload boundary to mandate the explicit usage of the `@skill:playwright-engineer`. 
**Example**: *"Implement the CRUD testing matrix, strictly utilizing the @skill:playwright-engineer parameter space."*

## 2. Infrastructure Determinism Constraint
Playwright tests are highly vulnerable to localized database cross-contamination and cyclomatic complexity limits. The QA Engineer MUST adhere to the following workflow bounds organically while drafting the Spec:
- **Teardown Loops**: You MUST verify that the Playwright execution explicitly implements the `pytest_deterministic_teardown.md` anti-pattern. SQLite environments (`.staging/*.db`) must be nuked between Pytest executions natively.
- **Complexity Isolation**: You MUST explicitly separate your Pytest `.fixture()` yields so that Test Server polling and DB bootstrapping are cleanly decoupled into distinct functions, guaranteeing a McCabe score $\le 5$.

## 3. Human-in-the-Loop Override
If the QA Engineer experiences >2 sequential `Playwright Timeout` or `<REDACTED_PHI>` trace failures, they MUST abort the testing matrix and natively escalate back to the Director to trigger `@workflow:human-in-the-loop` to inspect the visual HTML driver.
