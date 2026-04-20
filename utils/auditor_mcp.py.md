# Auditor MCP Server (`auditor_mcp.py`)

## Overview
This script implements a FastMCP server named "Auditor Validation Server". It acts as the ultimate gatekeeper for promoting or rejecting code mutations proposed by the agentic swarm, providing secure sandboxing via an isolated `.staging/` directory.

## Key Tools Provided

### `read_workspace_file(file_path: str)`
- **Purpose**: Securely reads files from the workspace.
- **Functionality**: Automatically intercepts read requests and redirects them to the `.staging/` airlock if a mutated version of a file exists. If it doesn't exist in staging, it falls back to the canonical file in the project workspace. Always strictly verified to prevent directory traversal outside the `project_root`.

### `promote_staging_area()`
- **Purpose**: Safely integrates approved agent code from the `.staging/` airlock back into the main `project_root`.
- **Security Check**: Employs a cryptographic physical authentication gate. The function requires an HMAC SHA-256 signed token (`.qa_signature`) present in the staging area (using `NGS_ZERO_TRUST_SIMULATION_KEY_2026`). This prevents Executor agents from forcibly hallucinating test assertions to bypass QA.
- **Action**: Uses a tightly restricted `rsync` subprocess to push code from the staging buffer directly to explicitly whitelisted organizational directories (e.g., `api/`, `orchestrator/`, `tests/`).

### `teardown_staging_area()`
- **Purpose**: Safely wipes the active `.staging/` workspace buffer.
- **Usage**: Invoked dynamically if the agentic workflows fail test-driven evaluations or architectural audits, cleanly resetting the environment without polluting the core source tree.
