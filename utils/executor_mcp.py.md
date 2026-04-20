# Executor MCP Proxy (`executor_mcp.py`)

## Overview
This script implements a complex FastMCP server titled "executor_mcp". It serves as the primary action-taking interface for the Swarm's Executor persona, built upon a high-security `.staging/` airlock paradigm to prevent destructive changes to the host Operating System.

## The `.staging/` Airlock Concept
The Executor is fundamentally restricted from writing to the raw physical workspace. Instead, it interacts with an ephemeral `.staging` shadow environment. Read commands evaluate `.staging` overlay files first, and all write mutations are trapped inside `.staging` to require secondary manual promotion by the QA Engineer/Auditor.

## Key Tools Provided

### Read / Search Operations
- **`read_workspace_file`**: Resolves read targets correctly by merging the `.staging` airlock state over the baseline code, truncating text blocks to preserve context budgets (`ADK_CONTEXT_SAFE_MODE`).
- **`list_workspace_directory`**: Seamlessly aggregates target directories across the airlock and baseline.
- **`search_workspace`**: Greps text matches accurately across both physical boundaries, returning properly formatted contextual lines.

### Mutational Operations
- **`write_workspace_file`**: Creates/mutates files entirely locked to the `.staging` environment. Enforces "Anti-Lazy Overwrite" rules, requiring explicit `overwrite=true` parameters to rewrite main logic files safely.
- **`replace_workspace_file_content`**: A deterministic surgical diff-replacement utility ensuring precise line-bound code patching in the airlock.
- **`append_workspace_file_content`**: Appends data strings directly to targets.

### Transient Sandboxing
- **`execute_transient_docker_sandbox`**: Escapes the restrictive constraints dynamically by automatically spawning an isolated `executor-sandbox:latest` Docker instance mounted strictly to the active `.staging/` buffer. This allows native test executions (e.g. `pytest`) of mutated code without granting the Swarm root shell access to the Developer's Mac OS environment.
- **`inspect_container_os_release`**: Scans targeted Docker image distributions securely over SSM.
