# AST-Based Context and Code-Reading Governance

This rule governs how agents read, analyze, and modify source files in the project workspace to maximize token efficiency, prevent context bloat, and verify architectural compliance.

## Core Mandates

### 1. AST Skeleton Priming
For any source file exceeding 100 lines, the agent MUST NOT load the entire file. Instead, the agent MUST first generate and inspect the file's AST skeleton using the native MCP server:
* **Tool:** `call_mcp_tool(ServerName="ast-context-mcp", ToolName="get_skeleton", Arguments={"file_path": "<file_path>"})`

This allows the agent to construct an interface-level blueprint of classes, methods, parameters, and docstrings for a fraction of the token cost.

### 2. Targeted Symbol Reading
If the skeleton indicates that only specific classes, functions, or variables are relevant to the implementation or analysis, the agent MUST load only those target blocks using:
* **Tool:** `call_mcp_tool(ServerName="ast-context-mcp", ToolName="get_symbol_block", Arguments={"file_path": "<file_path>", "symbol_name": "<symbol_name>"})`

### 3. Symbol Discovery
To obtain a quick, structured mapping of all symbols and line numbers in a file without loading its text:
* **Tool:** `call_mcp_tool(ServerName="ast-context-mcp", ToolName="get_symbols", Arguments={"file_path": "<file_path>"})`

### 4. Structural Pre-flight Checks
Before executing changes to any symbol signature, the agent MUST perform dependency impact analysis:
- Run static checks to identify all call sites referencing the target symbol.
- **AST Hash Comparison:** Verify current symbol or file hashes via `call_mcp_tool(ServerName="ast-context-mcp", ToolName="get_hash", Arguments={"file_path": "<file_path>", "symbol_name": "<symbol_name>"})`.

### 5. Precision Edits
When modifying code, edits MUST target only the code lines of the specific symbol being changed. Avoid broad, non-selective file rewrites to reduce token consumption and formatting conflicts.
