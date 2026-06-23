# AST Context MCP Server

This standalone, local Model Context Protocol (MCP) server provides token-efficient, formatting-independent **Abstract Syntax Tree (AST) parsing**, **skeleton extraction**, and **symbol isolation** for Python and TypeScript/JavaScript codebases.

Integrating this server into your agentic workflow (Cursor, Claude Code, Antigravity, etc.) immediately reduces agent input token consumption by up to **75%**, improves agent reasoning correctness, and speeds up iteration loops.

---

## Features & Mapped Tools

The server exposes four highly optimized tools designed to inspect codebases without polluting the LLM's context window:

1. **`get_symbols`**: Scans a `.py`, `.ts`, `.tsx`, `.js`, or `.jsx` file and returns a JSON array of all declared classes, interfaces, methods, functions, and types (along with their exact start/end line coordinates).
2. **`get_skeleton`**: Generates a structural outline of a file. It replaces all class/function implementation bodies with `pass` (Python) or placeholders (TypeScript/JS) while preserving decorators, signatures, type annotations, and docstrings.
3. **`get_symbol_block`**: Extracts the exact raw lines of code matching a specified symbol name (e.g., class, function, or method), filtering out the rest of the file.
4. **`get_hash`**: Computes a normalized, comment- and spacing-insensitive SHA-256 hash of a file or specific symbol. Useful for semantic change tracking and drift detection.

---

## Setup & Prerequisites

### Prerequisites
* **Python 3.11+** (using `uv` is highly recommended for speed and dependency isolation).
* **Node.js** (required to run the TypeScript parser subprocess).

### Installation

1. Install the required python MCP dependencies:
   ```bash
   pip install mcp fastmcp
   # Or using uv:
   uv pip install mcp fastmcp
   ```

2. Make sure you have the `typescript` package installed globally or locally:
   ```bash
   npm install -g typescript
   ```

---

## How to Integrate with Agentic Clients

### 1. Cursor IDE
To add this as a tool in Cursor:
1. Open Cursor Settings -> **Features** -> **MCP**.
2. Click **+ Add New MCP Server**.
3. Configure the server:
   * **Name**: `ast-context-mcp`
   * **Type**: `command`
   * **Command**: `uv run python /absolute/path/to/hvr-agentic-os/mcp_servers/ast_context_mcp/server.py`
4. Save. Cursor will start the server and register the tools.

### 2. Claude Code (CLI)
To register the server with Claude Code, run:
```bash
claude mcp add ast-context-mcp -- uv run python /absolute/path/to/hvr-agentic-os/mcp_servers/ast_context_mcp/server.py
```

### 3. Antigravity IDE (mcp_config.json)
Add the server entry to your `mcp_config.json`:
```json
{
  "mcpServers": {
    "ast-context-mcp": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/absolute/path/to/hvr-agentic-os/mcp_servers/ast_context_mcp/server.py"
      ]
    }
  }
}
```

---

## How It Works Under the Hood

The server acts as a polyglot coordinator:
* **Python Files (`.py`)** are parsed natively using Python's standard `ast` module. It uses custom AST walkers to extract skeletons, symbols, and compute docstring-free semantic hashes.
* **TypeScript/JavaScript Files (`.ts`, `.tsx`, `.js`, `.jsx`)** are delegated to the local `ts_ast_parser.js` utility, which compiles the source code into an AST using the official TypeScript Compiler API, ensuring perfect formatting-insensitive token stream hashing and signature extraction.
