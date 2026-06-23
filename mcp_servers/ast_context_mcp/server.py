#!/usr/bin/env python3
import os
import subprocess
import sys
import json
from mcp.server.fastmcp import FastMCP

# Ensure the local directory is in path to import ast_helpers
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

import ast_helpers as py_ast

mcp = FastMCP("ast-context-mcp")

# Dynamically resolve and verify paths based on the host's current working directory
WORKSPACE_ROOT = os.path.abspath(os.getcwd())

def _resolve_and_verify_path(file_path: str) -> str:
    """Resolves a file path and checks if it resides within the current workspace."""
    abs_path = os.path.abspath(file_path)
    if not abs_path.startswith(WORKSPACE_ROOT):
        raise ValueError(
            f"Security Error: File path '{file_path}' escapes workspace root '{WORKSPACE_ROOT}'"
        )
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: '{file_path}'")
    return abs_path

def _run_ts_parser(action: str, file_path: str, symbol_name: str = None) -> str:
    """Delegates parsing of TS/JS files to the local ts_ast_parser.js Node utility."""
    parser_path = os.path.join(SERVER_DIR, "ts_ast_parser.js")
    cmd = ["node", parser_path, action, file_path]
    if symbol_name:
        cmd.append(symbol_name)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr or f"TypeScript parser failed with exit code {result.returncode}"
        )
    return result.stdout

@mcp.tool()
def get_symbols(file_path: str) -> str:
    """
    List all classes, interfaces, methods, functions, and types in a Python or TypeScript/JavaScript file.
    Returns a JSON array of symbols.
    """
    try:
        abs_path = _resolve_and_verify_path(file_path)
    except Exception as e:
        return f"Error: {e}"
    
    _, ext = os.path.splitext(abs_path)
    if ext == ".py":
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                source = f.read()
            symbols = py_ast.extract_symbols(source)
            return json.dumps(symbols, indent=2)
        except Exception as e:
            return f"Error parsing Python file: {e}"
    elif ext in (".ts", ".tsx", ".js", ".jsx"):
        try:
            return _run_ts_parser("symbols", abs_path)
        except Exception as e:
            return f"Error parsing TypeScript file: {e}"
    else:
        return f"Error: Unsupported file extension '{ext}'."

@mcp.tool()
def get_skeleton(file_path: str) -> str:
    """
    Generate a structural skeleton of a Python or TypeScript/JavaScript file.
    Replaces function and method bodies with 'pass' or comments, preserving signatures and docstrings.
    """
    try:
        abs_path = _resolve_and_verify_path(file_path)
    except Exception as e:
        return f"Error: {e}"
    
    _, ext = os.path.splitext(abs_path)
    if ext == ".py":
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                source = f.read()
            return py_ast.generate_skeleton(source)
        except Exception as e:
            return f"Error generating Python skeleton: {e}"
    elif ext in (".ts", ".tsx", ".js", ".jsx"):
        try:
            return _run_ts_parser("skeleton", abs_path)
        except Exception as e:
            return f"Error generating TypeScript skeleton: {e}"
    else:
        return f"Error: Unsupported file extension '{ext}'."

@mcp.tool()
def get_symbol_block(file_path: str, symbol_name: str) -> str:
    """
    Retrieve the exact raw source code block for a specific symbol (class, method, or function)
    in a Python or TypeScript/JavaScript file.
    """
    try:
        abs_path = _resolve_and_verify_path(file_path)
    except Exception as e:
        return f"Error: {e}"
    
    _, ext = os.path.splitext(abs_path)
    if ext == ".py":
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                source = f.read()
            return py_ast.get_symbol_block(source, symbol_name)
        except Exception as e:
            return f"Error extracting Python symbol: {e}"
    elif ext in (".ts", ".tsx", ".js", ".jsx"):
        try:
            return _run_ts_parser("symbol-block", abs_path, symbol_name)
        except Exception as e:
            return f"Error extracting TypeScript symbol: {e}"
    else:
        return f"Error: Unsupported file extension '{ext}'."

@mcp.tool()
def get_hash(file_path: str, symbol_name: str = None) -> str:
    """
    Calculate the normalized, spacing- and comment-insensitive SHA-256 hash of a file or a specific symbol.
    Returns JSON metadata.
    """
    try:
        abs_path = _resolve_and_verify_path(file_path)
    except Exception as e:
        return f"Error: {e}"
    
    _, ext = os.path.splitext(abs_path)
    if ext == ".py":
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                source = f.read()
            h = py_ast.calculate_hash(source, symbol_name)
            return json.dumps({
                "file": os.path.relpath(abs_path, WORKSPACE_ROOT),
                "symbol": symbol_name,
                "hash": h,
                "algorithm": "sha256"
            }, indent=2)
        except Exception as e:
            return f"Error computing Python hash: {e}"
    elif ext in (".ts", ".tsx", ".js", ".jsx"):
        try:
            return _run_ts_parser("hash", abs_path, symbol_name)
        except Exception as e:
            return f"Error computing TypeScript hash: {e}"
    else:
        return f"Error: Unsupported file extension '{ext}'."


if __name__ == "__main__":
    mcp.run()
