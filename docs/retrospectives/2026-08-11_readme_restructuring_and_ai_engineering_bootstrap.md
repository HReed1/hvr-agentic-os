# Retrospective: README Restructuring & AI Engineering Bootstrap

**Date:** 2026-08-11  
**Commits:** `1904c2c`  
**Branch:** `doc_updates`

## Context/Objective

The root README had grown into a monolithic document mixing two audiences: ADK multi-agent swarm operators and developers adopting the portable AI Engineering scaffold (wiki, drift registry, sessions). The goal was to split it into two focused documents and create a proper bootstrap script for the AI Engineering layer.

A secondary goal was to clean up the legacy `bootstrap_agentic_os.sh` which scaffolded unused directories and a deprecated Vertex RAG config placeholder.

## Key Accomplishments

### README Split
- **Root README.md** — Complete rewrite focused on AI Engineering scaffold. Teaches users how to set up the LLM Wiki, Drift Registry, and Session Workflows in any repo. Includes a portability section ("Adopting in Your Own Repos") with a 5-step copy-and-run workflow.
- **agent_app/README.md** — New file containing all ADK-specific content: architecture diagram, agent roles, quick start, 11-test evaluation suite, zero-trust enforcement layers, Era 5 benchmarks, and firewall customization.

### New Bootstrap Script
- **bin/bootstrap_ai_engineering.sh** — Idempotent, non-destructive script that scaffolds `wiki/`, `docs/drift_registries/`, `.agents/`, `docs/retrospectives/`, and checks for Postgres availability. Prints a formatted, copyable LLM ingest prompt at the end instructing the agent to read the 3 reference guides in order.

### Legacy Cleanup
- **bin/bootstrap_agentic_os.sh** — Removed 4 unused scaffolding items: `docs/evals/retrospectives` (redundant), `vertex_rag_config.txt` (deprecated), and empty `src/`, `core/`, `etl/`, `infrastructure/` directories. Added cross-reference to the new AI Engineering bootstrap.

### Claim Correction
- **Removed 75% token reduction claim** from root README entirely (per previous session's audit establishing it as a mock-derived design parameter).

## Files Modified

### Created
- `agent_app/README.md` — Self-contained ADK multi-agent swarm documentation
- `bin/bootstrap_ai_engineering.sh` — AI Engineering scaffold bootstrapper

### Modified
- `README.md` — Complete rewrite for AI Engineering scaffold focus
- `bin/bootstrap_agentic_os.sh` — Legacy cleanup + cross-reference

## Drift Report

- **Agent**: 12/12 clean ✅
- **Docs**: 7/7 clean ✅
- **Infra**: 6/6 clean ✅
- **Wiki**: 30/30 clean (1 drifted from log.md update — intentional, stamped) ✅

## Decisions/Gotchas

1. **"Commands run from repo root" callout**: The `agent_app/README.md` quick start commands were initially generated with `../` relative paths (as if run from `agent_app/`). Corrected all paths and added an explicit note that all commands run from the repo root.

2. **Ingest prompt as heredoc**: The bootstrap's LLM prompt uses `cat << 'PROMPT'` heredoc syntax rather than echo statements. This preserves formatting, avoids shell escaping issues, and makes the prompt easily editable.

3. **Postgres is optional**: The bootstrap checks for `psql` and the `wiki` database but never auto-creates anything. Users who don't want the metadata index can skip Postgres entirely — the wiki works as plain markdown files.

4. **Feasibility discussion**: Before the README work, we had an honest discussion about the context benchmarking roadmap. The key insight: Antigravity agents don't expose input/output token counts, making a controlled A/B test of the AST context engineering infeasible with current tooling. The most viable approach is offline transcript analysis (measuring tool response size reduction as a proxy). Left open-ended for a future session.

## Carryover

1. **Drift registry entries for new files**: `agent_app/README.md` and `bin/bootstrap_ai_engineering.sh` should be registered in drift registries (likely `docs.json` and `infra.json` respectively)
2. **Wiki page for bootstrap**: Consider creating `wiki/entities/ai-engineering-bootstrap.md` documenting the scaffold setup process
3. **Test the bootstrap in a fresh repo**: Run `bootstrap_ai_engineering.sh` in an empty directory to verify the full scaffold works end-to-end
4. **Context benchmarking roadmap**: Offline transcript analysis approach deferred — decide if it's worth implementing
