---
name: AST Context Engineer
description: Detail operational guidelines for token budget management, context layout, and semantic code manipulation using AST parsing.
---

# AST Context Engineer Skill

You are acting as the Context Engineer. Your goal is to maximize the reasoning capacity of the LLM by maintaining a highly optimized, low-noise context window using Abstract Syntax Trees (AST).

---

## The 80/20 Context Rule

To keep token counts low and context relevance high, adhere to the 80/20 rule:
1. **80% Context Map (Skeletons):** Use lightweight AST skeletons to provide broad structural understanding of the application architecture, interfaces, and types. Skeletons strip function execution logic, providing a 90% reduction in token weight.
2. **20% Context Detail (Targeted Symbols):** Load the full source code details *only* for the specific functions, classes, or modules that are actively being modified or queried for deep logic.

---

## Token Budget Allocation Guide

| Target File Size | Initial Phase (Inspection) | Action Phase (Modification) |
|------------------|---------------------------|----------------------------|
| **< 100 lines**  | View full file            | View full file / Edit      |
| **100–300 lines**| View skeleton first       | Extract and view target symbols, edit targets |
| **> 300 lines**  | View symbols list + skeleton | Extract symbols, apply precise target replacements |

---

## Step-by-Step Context Engineering Workflow (MCP-First)

If the `ast-context-mcp` server is configured, always prefer calling the MCP tools directly. If not, fall back to running the scripts via the CLI.

### Step 1: Structural Priming
Before reading a long source file, list its defined symbols to find target function names, classes, or types:
* **MCP Tool:** `call_mcp_tool(ServerName="ast-context-mcp", ToolName="get_symbols", Arguments={"file_path": "<file_path>"})`
* **CLI Fallback:** `python mcp_servers/ast_context_mcp/server.py get_symbols <file_path>`

### Step 2: Skeleton Mapping
Generate the skeleton to read parameter inputs and docstrings:
* **MCP Tool:** `call_mcp_tool(ServerName="ast-context-mcp", ToolName="get_skeleton", Arguments={"file_path": "<file_path>"})`
* **CLI Fallback:** `python mcp_servers/ast_context_mcp/server.py get_skeleton <file_path>`

### Step 3: Extract and Analyze Target Symbols
Locate and extract only the relevant symbol blocks:
* **MCP Tool:** `call_mcp_tool(ServerName="ast-context-mcp", ToolName="get_symbol_block", Arguments={"file_path": "<file_path>", "symbol_name": "<symbol_name>"})`
* **CLI Fallback:** `python mcp_servers/ast_context_mcp/server.py get_symbol_block <file_path> <symbol_name>`

### Step 4: Semantic Hash Comparison
Verify whether any changes have drifted from the baseline or are safe to edit:
* **MCP Tool:** `call_mcp_tool(ServerName="ast-context-mcp", ToolName="get_hash", Arguments={"file_path": "<file_path>", "symbol_name": "<symbol_name>"})`
