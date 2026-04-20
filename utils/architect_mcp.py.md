# Architect MCP Proxy (`architect_mcp.py`)

## Overview
This script implements a standalone FastMCP server titled "Architect Secure IO Proxy". It is explicitly bound to the `@architect` persona to provide safe, structured file writing capabilities without exposing unfiltered bash environments to the agent.

## Key Tools Provided

### `write_architect_handoff(payload_json: str)`
- **Purpose**: Provides the Architect agent with a constrained, structured mechanism to dump analytical state schemas (`architect_handoff.json`). 
- **Security Posture**: Acts as a Zero-Trust gateway. It accepts a raw localized JSON payload string, validates its JSON schema conformity, enforces execution anchoring to the current working directory, and explicitly locks the write destination entirely to `artifacts/architect_handoff.json`. 
- **Effect**: Successfully prevents any directory traversal attacks, or potentially chaotic agent actions where agents might accidentally overwrite native configuration paths or source code during complex analysis.
