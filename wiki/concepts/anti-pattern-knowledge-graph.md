---
title: "Anti-Pattern Knowledge Graph"
date: 2026-06-02
category: concept
tags:
  - anti-patterns
  - knowledge
  - rag
  - testing
sources:
  - "[[docs/anti-patterns/asgi_playwright_latency.md]]"
  - "[[docs/anti-patterns/pytest_deterministic_teardown.md]]"
  - "[[docs/roadmap/2026-04-22_era4_autonomous_self_healing_roadmap.md]]"
last_ingested: 2026-06-02
---

# Anti-Pattern Knowledge Graph

The Anti-Pattern Knowledge Graph is a documented collection of known systemic quirks, testing pitfalls, and infrastructure failure modes that agents can reference to avoid repetitive hallucination death-loops.

## Architecture

Anti-patterns are stored as markdown files in `docs/anti-patterns/`. They are pre-loaded into the [[qa-engineer-agent]]'s static instruction context, enabling immediate pattern-matching when the agent encounters ambiguous errors.

## Documented Anti-Patterns

### ASGI Playwright Latency (`ERR_CONNECTION_REFUSED`)
**The Paradox**: Playwright boots headless Chromium in milliseconds, but Uvicorn takes up to 1s to bind to `127.0.0.1:8000`. Playwright attempts `page.goto()` before the server is reachable, causing false test failures.

**The Fix**: Inject a synchronous socket polling loop into the test fixture before yielding control to Playwright. Never alter backend routing logic to fix a testing race condition.

Source: [docs/anti-patterns/asgi_playwright_latency.md](../docs/anti-patterns/asgi_playwright_latency.md)

### Pytest Deterministic Teardown
**The Paradox**: In multi-step evaluations, SQLite databases persist between sequential `execute_tdaid_test` and `execute_coverage_report` runs. Duplicate data accumulates, causing Playwright strict-mode selector violations.

**The Fix**: All Pytest fixtures must implement `yield` teardowns that physically remove the testing database. State must reset to zero before the next Pytest worker initializes.

Source: [docs/anti-patterns/pytest_deterministic_teardown.md](../docs/anti-patterns/pytest_deterministic_teardown.md)

## Integration with Self-Healing (Era 4 Roadmap)

The [Era 4 Roadmap](../docs/roadmap/2026-04-22_era4_autonomous_self_healing_roadmap.md) envisions expanding the knowledge graph into a full RAG system with ADK's native `rag_tool`. When the QA Engineer encounters an unhandled exception, it would execute a RAG query against the anti-pattern database using the exception signature before mutating any backend code.

## See Also

- [[qa-engineer-agent]] — The primary consumer of anti-pattern knowledge
- [[evaluation-framework]] — Where anti-patterns most frequently manifest
- [[tdaid-methodology]] — The testing protocol anti-patterns inform
