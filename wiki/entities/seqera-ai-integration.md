---
title: "Seqera AI Integration"
date: 2026-06-02
category: entity
tags:
  - seqera
  - nextflow
  - nf-core
  - integration
  - bioinformatics
sources:
  - "[[docs/retrospectives/2026-04-29_seqera_ai_nfcore_emmtyper_pilot.md]]"
last_ingested: 2026-06-02
---

# Seqera AI Integration

The Seqera AI integration represents the first cross-agent integration between the [[agentic-os]] (Antigravity/Gemini) platform and an external domain-expert AI system. It enables the swarm to leverage Seqera AI's specialized knowledge of Nextflow pipelines, nf-core modules, and Wave containers.

## Architecture

The integration is **shell-based** via `run_command` → `seqera ai --headless`, deliberately avoiding MCP socket overhead. Seqera AI manages its own authentication (`seqera login`) and is self-contained with its own CLI.

### Invocation Patterns
Seven validated invocation patterns documented in `.agents/skills/seqera-ai-subagent/SKILL.md`:
1. Headless query
2. Sub-agent mode
3. Goal mode
4. Built-in skills
5. Wave containers
6. Module QA review
7. Session continuation

## Pilot: emmtyper Module PR

The integration was validated through the emmtyper nf-core module PR (#11377), which required 6 pushes to achieve green CI. Key lessons codified:

- Use `python -c import` for Python/Click version extraction (not `tool --version | sed`)
- Always use `sanitizeOutput()` in Nextflow test snapshots
- `meta.yml` is auto-generated — never hand-edit
- Run `restore_edam_comments.sh` after `nf-core modules lint --fix`

## Upstream Contribution

A documentation page was created at `seqeralabs-docs/platform-cloud/docs/seqera-ai/skill-antigravity.md` covering skill format, installation, and validated use cases.

## See Also

- [[agentic-os]] — The broader operating system
- [[evaluation-framework]] — Where integration tests would be validated
