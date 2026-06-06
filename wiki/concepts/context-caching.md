---
title: "Context Caching"
date: 2026-06-02
category: concept
tags:
  - optimization
  - performance
  - vertex-ai
  - adk
  - token-efficiency
sources:
  - "[[docs/retrospectives/2026-04-24_context_caching_optimization_results.md]]"
  - "[[docs/retrospectives/2026-04-24_era5_evaluation_integrity_restoration.md]]"
last_ingested: 2026-06-02
---

# Context Caching

Context Caching (Era 5.1) is the three-part optimization architecture that reduced the [[agentic-os]] swarm's token consumption by 56.3% and inference count by 44.1%, while expanding test coverage from 8 to 11 evaluations.

## Three Optimizations

### 1. Static/Dynamic Instruction Split
Each agent's prompt is divided into two fields:
- **`static_instruction`**: Agent identity, protocols, pre-loaded rules (~2–9KB). Tokenized **once** by Vertex AI and cached.
- **`instruction`** (via `InstructionProvider` callable): Dynamic per-turn content like the handoff ledger (~500B). Re-injected on every turn.

### 2. Vertex AI Context Caching
The root agent is wrapped in an `App` object with `ContextCacheConfig`:
```python
ContextCacheConfig(
    min_tokens=2048,      # Only cache if content > ~2K tokens
    ttl_seconds=1800,     # 30 min TTL (covers a full eval run)
    cache_intervals=15    # Refresh cache after 15 invocations
)
```
Static content is uploaded once as a cached prefix; subsequent requests reference it by ID.

### 3. Boot-Read Elimination
All `.agents/rules/*.md` files (~17KB total) are pre-loaded at Python import time via `load_rules()` and injected into the [[director-agent]]'s static instruction. This eliminates the 3–4 `list_docs → read_doc` inferences previously spent on every run.

## Impact

| Metric | Before (Apr 23) | After (Apr 24) | Delta |
|--------|:---:|:---:|:---:|
| Total Inferences (7 matched tests) | 213 | 119 | **−44.1%** |
| Total Input Tokens | 3,487,199 | 1,514,945 | **−56.6%** |
| Total Tokens | 3,509,057 | 1,528,329 | **−56.4%** |

The compounding effect: for a Director with ~35KB of static content making 2 inferences, tokenized cost dropped from 70KB to ~36KB (−49%). For an Executor making 8 turns, from 56KB to ~11KB (−80%).

## Lesson

> `static_instruction` is the single highest-impact optimization. Moving content from `instruction` to `static_instruction` reduced input tokens by over 50% with zero behavioral change.

## See Also

- [[token-tax]] — The original problem context caching helps mitigate
- [[evaluation-framework]] — Where the optimization impact is measured
- [[director-agent]] — The agent with the largest pre-loaded context
