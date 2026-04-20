---
name: ast-dependency-mapper
description: Read-only DAG traversal tool to visually map Nextflow channel routings and output dimensions.
---

# AST Dependency Mapper

**Purpose:** Allows the Architect to "see" exactly which channels will geometrically starve if a specific process tuple output is modified.

## When to use this skill
* Before approving any Nextflow structural additions or channel manipulations in new process directives.
* To assess DAG topologies without triggering active Pytest assertion tests.

## How to use it
* Execute `python3 .agents/skills/ast-dependency-mapper/mapper.py <TARGET_PROCESS>`.
* This tool is strictly **READ-ONLY**. It parses the textual AST of `.nf` files and outputs a text-based dependency tree mapping.
* Use the resulting visual tree to verify asynchronous channel alignment (e.g. `.groupTuple()` outputs) before drafting a mutation directive.
