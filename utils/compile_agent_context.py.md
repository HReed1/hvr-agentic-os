# Compile Agent Context (`compile_agent_context.py`)

## Overview
This Python script serves as the centralized Bootstrap compiler for "Forced Context Injection". It manages the LLM context windows by dynamically assembling system rules and operational history so they can be natively mounted into the Executor or Architect payloads.

## Functionality
- **Context Scraping**: Crawls `.agents/rules/*.md` and `docs/retrospectives/*.md`.
- **Systematic Ranking**: Hardcodes the positioning of crucial rules (`cli-context-mandate.md`, `nextflow-orchestration.md`, `infrastructure-as-code.md`) at the very top of the compiled layout to prevent the underlying LLM from experiencing context amnesia regarding fundamental operating boundaries.
- **Truncation**: Only pulls the 4 most recent files from the `docs/retrospectives/` directory to prevent unbounded context ballooning.
- **Output Generation**: Combines the extracted rules and retrospectives into a single master payload written to `.agents/compiled_context.md`.
