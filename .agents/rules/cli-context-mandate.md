---
description: Enforces explicit cross-referencing against internal tool contexts before proposing containerized CLI logic.
glob: "*.nf, *.sh"
---

# The CLI Context Mandate

1. Before modifying, writing, or executing any bash execution blocks involving CLI tools (e.g., `samtools`, `sambamba`, `bwa`, `minimap2`), you **MUST** natively cross-reference your internal knowledge against `docs/gemini/CONTEXT_CLI_REFERENCE.md` and `docs/gemini/CONTEXT_CONTAINER_REGISTRY.md`.
2. **Container Transparency**: You are strictly forbidden from guessing positional arguments or blindly assuming standard public binaries (like `sambamba`) exist inside generic `ngs-bcftools` containers. If a tool isn't listed in the Container Registry for a specific container, the pipeline will crash with `Exit 127`. Validate first.
