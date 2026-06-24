import ast
import os
import subprocess
from typing import Optional

from context_benchmarking.analyzer import OfflineAnalyzer


def grep_search(query: str, path: str, repo_path: str = ".") -> str:
    """
    Recursively searches for occurrences of a query string inside files at the given path.
    Only searches text files, skipping binary files and common build/hidden directories.

    Args:
        query: The search term.
        path: File or directory path to search.
        repo_path: The base repository path to resolve relative paths.

    Returns:
        str: A string of matches in ripgrep style: "relative_path:line_number: line_content".
    """
    target_path = os.path.abspath(path)
    abs_repo = os.path.abspath(repo_path)

    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Path does not exist: {path}")

    matches = []

    def search_single_file(file_path: str):
        # Quick binary file check
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                if b"\x00" in chunk:
                    return  # Binary file, skip
        except Exception:
            return

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_idx, line in enumerate(f, 1):
                    if query in line:
                        rel_file = os.path.relpath(file_path, abs_repo)
                        matches.append(f"{rel_file}:{line_idx}: {line.rstrip(chr(10))}")
        except Exception:
            pass

    if os.path.isfile(target_path):
        search_single_file(target_path)
    else:
        for root, dirs, files in os.walk(target_path):
            # Prune hidden folders and common cache/dependency directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d
                not in ("__pycache__", "node_modules", "dist", "build", "venv", "env", "results")
            ]
            for file in files:
                search_single_file(os.path.join(root, file))

    if not matches:
        return f"No matches found for query: '{query}'"
    return "\n".join(matches)


def view_file(
    path: str, start_line: Optional[int] = None, end_line: Optional[int] = None
) -> str:
    """
    Reads the file content (optionally in a line range) and prefixes each line with its 1-based line number.
    Format: "   1: line content" (4-character width-aligned line number).

    Args:
        path: Path to the file.
        start_line: Optional 1-based start line.
        end_line: Optional 1-based end line.

    Returns:
        str: Prefixed file content.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    if os.path.isdir(path):
        raise IsADirectoryError(f"Path is a directory: {path}")

    lines = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, 1):
            if start_line is not None and line_num < start_line:
                continue
            if end_line is not None and line_num > end_line:
                continue
            lines.append(f"{line_num:4}: {line.rstrip(chr(10))}")

    return "\n".join(lines)


def _run_ts_parser(action: str, file_path: str, symbol_name: Optional[str] = None) -> str:
    parser_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ts_ast_parser.js")
    cmd = ["node", parser_path, action, file_path]
    if symbol_name:
        cmd.append(symbol_name)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or f"TypeScript parser failed with exit code {result.returncode}")
    return result.stdout


def get_symbols(file_path: str) -> str:
    """
    List all classes, interfaces, methods, functions, and types in a Python or TypeScript/JavaScript file.
    Returns a JSON array of symbols.

    Args:
        file_path: Path to the target source file.

    Returns:
        str: JSON string of symbols.
    """
    import json
    target_path = os.path.abspath(file_path)
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if os.path.isdir(target_path):
        raise IsADirectoryError(f"Path is a directory: {file_path}")

    _, ext = os.path.splitext(target_path.lower())
    if ext in (".ts", ".tsx", ".js", ".jsx"):
        try:
            return _run_ts_parser("symbols", target_path)
        except Exception as e:
            return f"Error: {e}"

    with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    analyzer = OfflineAnalyzer()
    symbols = analyzer.extract_symbols(code)
    return json.dumps(symbols, indent=2)


def get_skeleton(file_path: str) -> str:
    """
    Generates an AST-based skeleton of the file, stripping implementation blocks
    while retaining structural definitions (e.g. classes, methods, docstrings).
    Uses OfflineAnalyzer.

    Args:
        file_path: Path to the target source file.

    Returns:
        str: The generated AST skeleton.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if os.path.isdir(file_path):
        raise IsADirectoryError(f"Path is a directory: {file_path}")

    _, ext = os.path.splitext(file_path.lower())
    if ext in (".ts", ".tsx", ".js", ".jsx"):
        try:
            return _run_ts_parser("skeleton", file_path)
        except Exception as e:
            return f"Error: {e}"

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    analyzer = OfflineAnalyzer()
    return analyzer.generate_ast_skeleton(code, file_path=file_path)


def get_symbol_block(file_path: str, symbol_name: str) -> str:
    """
    Retrieves the specific block of code defining the target symbol inside the file.
    Uses OfflineAnalyzer.

    Args:
        file_path: Path to the target source file.
        symbol_name: The class or function name (short or fully-qualified).

    Returns:
        str: The code block for the symbol.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if os.path.isdir(file_path):
        raise IsADirectoryError(f"Path is a directory: {file_path}")

    _, ext = os.path.splitext(file_path.lower())
    if ext in (".ts", ".tsx", ".js", ".jsx"):
        try:
            return _run_ts_parser("symbol-block", file_path, symbol_name)
        except Exception as e:
            raise ValueError(f"Symbol '{symbol_name}' not found in file: {file_path} (TS parser error: {e})")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    analyzer = OfflineAnalyzer()
    block = analyzer.get_symbol_block(code, symbol_name)
    if block is None:
        raise ValueError(f"Symbol '{symbol_name}' not found in file: {file_path}")
    return block


def query_codebase_graph(symbol: str, repo_path: str = ".") -> str:
    """
    Performs static analysis across Python files in the codebase to map definitions
    and references for a given symbol, extracting import links and calls.

    Args:
        symbol: The name of the symbol to query.
        repo_path: Root directory of the codebase.

    Returns:
        str: Structural mapping of definitions and references.
    """
    abs_repo = os.path.abspath(repo_path)
    if not os.path.exists(abs_repo):
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    definitions = []
    references = []

    # Split symbol to handle qualified names
    symbol_parts = symbol.split(".")
    short_name = symbol_parts[-1]

    for root, dirs, files in os.walk(abs_repo):
        # Prune hidden folders and common cache/dependency directories
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d not in ("__pycache__", "node_modules", "dist", "build", "venv", "env")
        ]

        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, abs_repo)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                tree = ast.parse(content)
            except Exception:
                continue

            class GraphVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.class_stack = []

                def visit_ClassDef(self, node):
                    self.class_stack.append(node.name)
                    fq_name = ".".join(self.class_stack)

                    if node.name == symbol or fq_name == symbol:
                        definitions.append(
                            {
                                "path": rel_path,
                                "line": node.lineno,
                                "type": "class",
                                "name": fq_name,
                            }
                        )
                    self.generic_visit(node)
                    self.class_stack.pop()

                def visit_FunctionDef(self, node):
                    fq_name = ".".join(self.class_stack + [node.name])

                    if node.name == symbol or fq_name == symbol:
                        definitions.append(
                            {
                                "path": rel_path,
                                "line": node.lineno,
                                "type": "method" if self.class_stack else "function",
                                "name": fq_name,
                            }
                        )
                    self.generic_visit(node)

                def visit_AsyncFunctionDef(self, node):
                    self.visit_FunctionDef(node)

                def visit_Name(self, node):
                    if node.id == short_name and isinstance(node.ctx, ast.Load):
                        references.append(
                            {
                                "path": rel_path,
                                "line": node.lineno,
                                "type": "name_reference",
                            }
                        )
                    self.generic_visit(node)

                def visit_Attribute(self, node):
                    if node.attr == short_name:
                        references.append(
                            {
                                "path": rel_path,
                                "line": node.lineno,
                                "type": "attribute_reference",
                            }
                        )
                    self.generic_visit(node)

                def visit_Import(self, node):
                    for name in node.names:
                        if (
                            name.name == symbol
                            or name.name.split(".")[-1] == short_name
                        ):
                            references.append(
                                {
                                    "path": rel_path,
                                    "line": node.lineno,
                                    "type": "import",
                                }
                            )

                def visit_ImportFrom(self, node):
                    if node.module and (
                        symbol in node.module
                        or any(n.name == short_name for n in node.names)
                    ):
                        references.append(
                            {"path": rel_path, "line": node.lineno, "type": "import"}
                        )

            visitor = GraphVisitor()
            visitor.visit(tree)

    # Filter references to exclude the exact definition locations
    def_locations = {(d["path"], d["line"]) for d in definitions}
    unique_refs = []
    seen_refs = set()

    for r in references:
        loc = (r["path"], r["line"])
        if loc not in def_locations and loc not in seen_refs:
            unique_refs.append(r)
            seen_refs.add(loc)

    # Construct output
    lines = []
    lines.append(f"Codebase Graph Query for Symbol: '{symbol}'")
    lines.append("-" * len(lines[0]))

    lines.append("\nDefinitions:")
    if definitions:
        for d in definitions:
            lines.append(
                f"  - {d['path']}:{d['line']} ({d['type']} definition: {d['name']})"
            )
    else:
        lines.append("  (None found)")

    lines.append("\nReferences:")
    if unique_refs:
        for r in unique_refs:
            lines.append(f"  - {r['path']}:{r['line']} ({r['type']})")
    else:
        lines.append("  (None found)")

    return "\n".join(lines)


def write_to_file(path: str, content: str) -> str:
    """
    Writes or overwrites the full content of a target file.

    Args:
        path: Path to the target file.
        content: The text content to write.

    Returns:
        str: A success message.
    """
    dir_name = os.path.dirname(os.path.abspath(path))
    os.makedirs(dir_name, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully wrote content to: {path}"


def replace_file_content(
    path: str,
    target: str,
    replacement: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
) -> str:
    """
    Replaces a specific target code block in a file with replacement content.
    If start_line and end_line are provided (1-based), restricts the search/replacement to those lines.

    Args:
        path: Path to the target file.
        target: The text block to replace.
        replacement: The replacement content.
        start_line: Optional 1-based start line of target block.
        end_line: Optional 1-based end line of target block.

    Returns:
        str: A success message.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    if start_line is not None and end_line is not None:
        lines = content.splitlines(keepends=True)
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)

        target_subsegment = "".join(lines[start_idx:end_idx])
        if target not in target_subsegment:
            raise ValueError(
                f"Target text not found in lines {start_line}-{end_line} of {path}"
            )

        new_subsegment = target_subsegment.replace(target, replacement)
        lines[start_idx:end_idx] = [new_subsegment]
        new_content = "".join(lines)
    else:
        if target not in content:
            raise ValueError(f"Target text not found in file: {path}")
        new_content = content.replace(target, replacement)

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return f"Successfully replaced target content in: {path}"
