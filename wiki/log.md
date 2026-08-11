---
title: "Wiki Activity Log"
date: 2026-05-29
category: log
tags:
  - wiki
  - changelog
---

# Wiki Activity Log — hvr-agentic-os

> Chronological record of all wiki operations (ingest, query, lint).

## [2026-05-29] bootstrap | Initial Wiki Setup
- Source: Documentation restructuring initiative
- Created: [[index]], [[log]], [[overview]]
- Key insight: Wiki layer established as agent-maintained knowledge base over restructured docs/

## [2026-06-02] ingest | First Major Wiki Ingest — Full Source Material Bootstrap
- Sources ingested:
  - `docs/retrospectives/2026-04-23_hvr_agentic_os_meta_retrospective.md`
  - `docs/retrospectives/2026-04-20_zero_trust_stabilization_and_telemetry.md`
  - `docs/retrospectives/2026-04-21_head_to_head_benchmarks.md`
  - `docs/retrospectives/2026-04-22_hierarchical_routing_pivot.md`
  - `docs/retrospectives/2026-04-22_hierarchical_swarm_triumph.md`
  - `docs/retrospectives/2026-04-22_the_swarm_crucible_retrospective.md`
  - `docs/retrospectives/2026-04-23_agentic_os_drift_analysis.md`
  - `docs/retrospectives/2026-04-23_iterative_macro_looping.md`
  - `docs/retrospectives/2026-04-23_kernel_graft_and_tdaid_stabilization.md`
  - `docs/retrospectives/2026-04-23_orchestration_stabilization_retrospective.md`
  - `docs/retrospectives/2026-04-24_context_caching_optimization_results.md`
  - `docs/retrospectives/2026-04-24_era5_evaluation_integrity_restoration.md`
  - `docs/retrospectives/2026-04-24_era_5_head_to_head_conclusion.md`
  - `docs/retrospectives/2026-04-25_tool_parallelism_bottleneck_analysis.md`
  - `docs/retrospectives/2026-04-26_adk_2_0_iterative_refinement_migration.md`
  - `docs/retrospectives/2026-04-29_seqera_ai_nfcore_emmtyper_pilot.md`
  - `docs/decisions/2026-04-23_Spec-Driven_TDD_implementation_plan.md`
  - `docs/decisions/2026-04-23_tdaid_refactor_directive.md`
  - `docs/anti-patterns/asgi_playwright_latency.md`
  - `docs/anti-patterns/pytest_deterministic_teardown.md`
  - `docs/guides/2026-04-21_full-stack_benchmark_walkthrough.md`
  - `docs/guides/2026-04-21_head_to_head_evaluation_walkthrough.md`
  - `docs/roadmap/2026-04-22_era4_autonomous_self_healing_roadmap.md`
  - `docs/roadmap/2026-04-23_social_media_manager_roadmap.md`
- Created (12 entities):
  - [[agentic-os]] — The Zero-Trust Multi-Agent OS itself
  - [[director-agent]] — Top-level orchestration node
  - [[executor-agent]] — Code mutation engine
  - [[qa-engineer-agent]] — Adversarial test gate
  - [[zero-trust-auditor]] — Final deployment gate
  - [[staging-airlock]] — The `.staging/` sandbox
  - [[zero-trust-interceptors]] — `zero_trust.py` signal routing
  - [[dlp-proxy]] — PHI/HIPAA redaction layer
  - [[evaluation-framework]] — Automated benchmarking infrastructure
  - [[telemetry-engine]] — Trace extraction and reporting
  - [[seqera-ai-integration]] — Nextflow/nf-core cross-agent integration
  - [[drift-registry]] — Cross-file dependency tracking
- Created (10 concepts):
  - [[tdaid-methodology]] — Test-Driven AI Development protocol
  - [[token-tax]] — Context bloat from shared conversations
  - [[context-caching]] — Static/dynamic instruction split (56% token reduction)
  - [[amnesia-sweep]] — `git clean -fd` defense protocol
  - [[tool-parallelism-bottleneck]] — Irreducible ~4× multi-agent overhead
  - [[solo-vs-swarm-benchmarks]] — Empirical Solo vs Swarm comparison
  - [[hierarchical-routing]] — SequentialAgent tree architecture
  - [[anti-pattern-knowledge-graph]] — Documented systemic failure modes
  - [[ephemeral-memory-handoff]] — Cross-session `executor_handoff.md` persistence
  - [[empirical-verification]] — No-assumptions debugging methodology
- Updated: [[index]], [[overview]]
- Key insight: 24 source documents synthesized into 22 wiki pages (12 entities, 10 concepts) covering the complete architectural evolution from ADK monkey-patch through Era 5 context caching and empirical benchmarking

## [2026-06-02] lint | Post-Ingest Validation
- Orphans found: 0
- Broken wikilinks found: 1 → fixed
  - `[[development-workflow]]` in [[director-agent]] → replaced with `development_workflow` code reference + link to [[hierarchical-routing]]
- Contradictions found: 1 (Architect agent) → fixed across 3 files
  - [[overview]]: Removed `architect_agent` from tree diagram, added decommission note
  - [[token-tax]]: Annotated Architect as `[since decommissioned]` in historical context
  - [[hierarchical-routing]]: Removed `architect_agent` from `SequentialAgent` code diagram, documented Era 4 decommission with source citation
- Stale pages: 0
- Missing pages suggested: 0
- Auto-fixed: 4 edits across 4 files (overview.md, token-tax.md, hierarchical-routing.md, director-agent.md)

## [2026-08-11] ingest | v2.0.0 & Post-Release Wiki Coverage Expansion
- Source: `docs/reference/llm-wiki-antigravity.md`, `mcp_servers/ast_context_mcp/README.md`, `.agents/workflows/session-start.md`, `.agents/workflows/session-wrapup.md`, `scripts/drift_enforcer.py`
- Created (5 entities):
  - [[llm-wiki]] — Postgres-backed LLM Wiki (Karpathy pattern), v2.0.0 Pillar 1
  - [[drift-enforcer]] — Git-hash drift enforcement script, v2.0.0 Pillar 2
  - [[session-lifecycle]] — Structured session workflows, v2.0.0 Pillar 3
  - [[ast-context-mcp]] — FastMCP AST parsing server (post-v2.0.0, unreleased)
  - [[context-benchmarking]] — Agent context engineering test harness (post-v2.0.0, unreleased)
- Updated: [[overview]], [[index]]
- Key insight: v2.0.0 introduced 3 pillars (wiki, drift, sessions) and post-release work added AST-based context engineering — expanding wiki from 12 to 17 entity pages

## [2026-08-11] fix | llm-wiki-antigravity.md Schema Drift Resolution
- Source: `docs/reference/llm-wiki-antigravity.md`
- Updated: `wiki_links` schema to add `context TEXT`, `created_at TIMESTAMP`, and `supersedes` link type — matching the actual `wiki_db_init.py` implementation
- Key insight: Reference guide was out of sync with the deployed init script since commit 2d0103c

## [2026-08-11] fix | Wiki.json Registry Coverage Completion
- Source: N/A (registry maintenance)
- Updated: wiki.json drift registry — added 6 untracked pages
- Pages registered: [[amnesia-sweep]], [[llm-wiki]], [[drift-enforcer]], [[session-lifecycle]], [[ast-context-mcp]], [[context-benchmarking]]
- Fixed 3 wiki pages with incorrect source paths (docs/ prefix removal)
- Key insight: wiki.json now has 30 entries with 100% coverage of all entity/concept pages

## [2026-08-11] ingest | AST MCP & Context Benchmarking Retrospective
- Source: `docs/retrospectives/2026-06-23_ast_mcp_and_context_benchmarking.md`
- Created: Formal retrospective for commit 69ef905 (9,749 lines)
- Updated: [[context-benchmarking]] — replaced coverage gap notice with documentation section
- Key insight: Harness uses mock LLM monkeypatching for deterministic offline benchmarks (75% figure is a design parameter, not measured)

## [2026-08-11] fix | Benchmarking Accuracy Audit
- Source: `docs/retrospectives/2026-08-11_benchmarking_accuracy_audit.md`
- Updated: [[context-benchmarking]], [[ast-context-mcp]], overview.md, index.md
- Key corrections:
  - 75% token reduction is a hardcoded mock parameter (`run_benchmarks.py:503`), not an empirical measurement
  - 3 core modules (`simulator.py`, `analyzer.py`, `tools.py`) are missing — real pipeline cannot execute
  - ~7 of 12 test files would fail on import
- Roadmap added: implement missing modules → run live inference → validate claims independently

## [2026-08-11] ingest | README Restructuring & AI Engineering Bootstrap
- Source: `docs/retrospectives/2026-08-11_readme_restructuring_and_ai_engineering_bootstrap.md`
- Updated: [[overview]] (project description now references portable scaffold)
- Key insight: Split root README into AI Engineering scaffold guide (portable) and ADK swarm guide (project-specific). Created `bin/bootstrap_ai_engineering.sh` with LLM ingest prompt for initializing wiki + drift + sessions in any repo.
