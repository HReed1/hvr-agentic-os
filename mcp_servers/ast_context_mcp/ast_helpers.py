#!/usr/bin/env python3
"""
ast_helpers.py

Helper utilities to parse Python source code using the standard `ast` module,
extract symbols/metadata, generate normalized semantic hashes, create skeletons,
and retrieve raw source blocks for target symbols.
"""

import ast
import hashlib
import json
import os
import sys
import copy
from typing import List, Dict, Any, Optional, Tuple


def classify_class(node: ast.ClassDef) -> str:
    """Classify class definition into 'class', 'interface', or 'enum'."""
    for base in node.bases:
        base_id = None
        base_attr = None
        base_value_id = None

        if isinstance(base, ast.Name):
            base_id = base.id
        elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
            base_value_id = base.value.id
            base_attr = base.attr
        elif isinstance(base, ast.Subscript):
            if isinstance(base.value, ast.Name):
                base_id = base.value.id
            elif isinstance(base.value, ast.Attribute) and isinstance(
                base.value.value, ast.Name
            ):
                base_value_id = base.value.value.id
                base_attr = base.value.attr

        # Check Enum
        if base_id in ("Enum", "IntEnum", "StrEnum", "Flag"):
            return "enum"
        if base_value_id == "enum" and base_attr in (
            "Enum",
            "IntEnum",
            "StrEnum",
            "Flag",
        ):
            return "enum"

        # Check Interface / Protocol
        if base_id in ("Protocol", "ABC"):
            return "interface"
        if base_value_id in ("typing", "abc") and base_attr in ("Protocol", "ABC"):
            return "interface"

    # Heuristic names
    if "Interface" in node.name or "Protocol" in node.name:
        return "interface"

    return "class"


def is_type_alias_or_var(node: ast.AST) -> Optional[str]:
    """Check if node represents a type alias or TypeVar declaration. Returns the name if True."""
    # 1. PEP 695 (Python 3.12+)
    if hasattr(ast, "TypeAlias") and isinstance(node, ast.TypeAlias):
        if isinstance(node.name, ast.Name):
            return node.name.id

    # 2. AnnAssign (e.g. MyAlias: TypeAlias = ...)
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        annotation = node.annotation
        is_alias = False
        if isinstance(annotation, ast.Name) and annotation.id == "TypeAlias":
            is_alias = True
        elif isinstance(annotation, ast.Attribute) and isinstance(
            annotation.value, ast.Name
        ):
            if (
                annotation.value.id in ("typing", "typing_extensions")
                and annotation.attr == "TypeAlias"
            ):
                is_alias = True
        if is_alias:
            return node.target.id

    # 3. Assign (e.g. T = TypeVar('T'), Alias = Union[int, str])
    if (
        isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
    ):
        target_name = node.targets[0].id
        val = node.value
        # TypeVar or NewType call
        if isinstance(val, ast.Call):
            func = val.func
            if isinstance(func, ast.Name) and func.id in ("TypeVar", "NewType"):
                return target_name
            elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id == "typing" and func.attr in ("TypeVar", "NewType"):
                    return target_name

    return None


class SymbolVisitor(ast.NodeVisitor):
    """AST visitor to collect symbols with their qualified names and ranges."""

    def __init__(self):
        self.symbols: List[Dict[str, Any]] = []
        self.scope_stack: List[Tuple[str, str]] = []  # list of (scope_type, scope_name)

    def get_qname(self, name: str) -> str:
        names = [item[1] for item in self.scope_stack] + [name]
        return ".".join(names)

    def get_parent_type(self) -> Optional[str]:
        if self.scope_stack:
            return self.scope_stack[-1][0]
        return None

    def visit_ClassDef(self, node: ast.ClassDef):
        symbol_type = classify_class(node)
        qname = self.get_qname(node.name)

        start_line = node.lineno
        if node.decorator_list:
            start_line = min(start_line, node.decorator_list[0].lineno)

        self.symbols.append(
            {
                "name": node.name,
                "qname": qname,
                "type": symbol_type,
                "start_line": start_line,
                "end_line": node.end_lineno,
            }
        )

        self.scope_stack.append(("class", node.name))
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.handle_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.handle_function(node)

    def handle_function(self, node: ast.AST):
        name = node.name
        parent_type = self.get_parent_type()
        symbol_type = "method" if parent_type == "class" else "function"
        qname = self.get_qname(name)

        start_line = node.lineno
        if node.decorator_list:
            start_line = min(start_line, node.decorator_list[0].lineno)

        self.symbols.append(
            {
                "name": name,
                "qname": qname,
                "type": symbol_type,
                "start_line": start_line,
                "end_line": node.end_lineno,
            }
        )

        self.scope_stack.append(("function", name))
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_Assign(self, node: ast.Assign):
        name = is_type_alias_or_var(node)
        if name:
            qname = self.get_qname(name)
            self.symbols.append(
                {
                    "name": name,
                    "qname": qname,
                    "type": "type",
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                }
            )
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        name = is_type_alias_or_var(node)
        if name:
            qname = self.get_qname(name)
            self.symbols.append(
                {
                    "name": name,
                    "qname": qname,
                    "type": "type",
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                }
            )
        self.generic_visit(node)

    def visit_TypeAlias(self, node: ast.AST):
        name = is_type_alias_or_var(node)
        if name:
            qname = self.get_qname(name)
            self.symbols.append(
                {
                    "name": name,
                    "qname": qname,
                    "type": "type",
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                }
            )
        self.generic_visit(node)


def extract_symbols(source: str) -> List[Dict[str, Any]]:
    """Parse source and return JSON serializable symbols list."""
    tree = ast.parse(source)
    visitor = SymbolVisitor()
    visitor.visit(tree)
    return visitor.symbols


def strip_docstrings(node: ast.AST) -> None:
    """In-place recursively remove docstrings from module, class, and function nodes."""
    for child in ast.walk(node):
        if isinstance(
            child, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            if child.body:
                first = child.body[0]
                is_docstring = False
                if isinstance(first, ast.Expr):
                    if isinstance(first.value, ast.Constant) and isinstance(
                        first.value.value, str
                    ):
                        is_docstring = True
                    elif (
                        hasattr(ast, "Str")
                        and isinstance(first.value, ast.Str)
                        and isinstance(first.value.s, str)
                    ):
                        is_docstring = True

                if is_docstring:
                    child.body = child.body[1:]
                    if not child.body:
                        child.body = [ast.Pass()]


class SkeletonTransformer(ast.NodeTransformer):
    """Transforms AST by replacing function bodies with pass, preserving docstrings."""

    def visit_FunctionDef(self, node: ast.FunctionDef):
        docstring_node = None
        if node.body:
            first = node.body[0]
            is_docstring = False
            if isinstance(first, ast.Expr):
                if isinstance(first.value, ast.Constant) and isinstance(
                    first.value.value, str
                ):
                    is_docstring = True
                elif (
                    hasattr(ast, "Str")
                    and isinstance(first.value, ast.Str)
                    and isinstance(first.value.s, str)
                ):
                    is_docstring = True

            if is_docstring:
                docstring_node = first

        if docstring_node:
            node.body = [docstring_node, ast.Pass()]
        else:
            node.body = [ast.Pass()]
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        return self.visit_FunctionDef(node)


def generate_skeleton(source: str) -> str:
    """Returns the plain-text skeleton of the source code."""
    tree = ast.parse(source)
    transformer = SkeletonTransformer()
    transformer.visit(tree)
    return ast.unparse(tree)


def locate_node_by_qname(tree: ast.AST, target_qname: str) -> Optional[ast.AST]:
    """Finds the AST node corresponding to a specific qualified name."""
    stack: List[str] = []
    found_node: Optional[ast.AST] = None

    class Finder(ast.NodeVisitor):
        def visit_ClassDef(self, node):
            nonlocal found_node
            qname = ".".join(stack + [node.name])
            if qname == target_qname:
                found_node = node
                return
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        def visit_FunctionDef(self, node):
            nonlocal found_node
            qname = ".".join(stack + [node.name])
            if qname == target_qname:
                found_node = node
                return
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)

        def visit_Assign(self, node):
            nonlocal found_node
            name = is_type_alias_or_var(node)
            if name:
                qname = ".".join(stack + [name])
                if qname == target_qname:
                    found_node = node
                    return
            self.generic_visit(node)

        def visit_AnnAssign(self, node):
            nonlocal found_node
            name = is_type_alias_or_var(node)
            if name:
                qname = ".".join(stack + [name])
                if qname == target_qname:
                    found_node = node
                    return
            self.generic_visit(node)

        def visit_TypeAlias(self, node):
            nonlocal found_node
            name = is_type_alias_or_var(node)
            if name:
                qname = ".".join(stack + [name])
                if qname == target_qname:
                    found_node = node
                    return
            self.generic_visit(node)

    Finder().visit(tree)
    return found_node


def get_normalized_ast_hash(source: str, symbol_name: Optional[str] = None) -> str:
    """Generates the SHA-256 semantic hash of source or a target symbol."""
    tree = ast.parse(source)

    if symbol_name:
        node = locate_node_by_qname(tree, symbol_name)
        if not node:
            raise ValueError(f"Symbol '{symbol_name}' not found in source.")
        target_node = copy.deepcopy(node)
    else:
        target_node = copy.deepcopy(tree)

    strip_docstrings(target_node)

    dumped = ast.dump(target_node, include_attributes=False)
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()


calculate_hash = get_normalized_ast_hash


def get_symbol_block(source: str, symbol_name: str) -> str:
    """Returns the raw source code lines corresponding to the target symbol."""
    tree = ast.parse(source)
    node = locate_node_by_qname(tree, symbol_name)
    if not node:
        raise ValueError(f"Symbol '{symbol_name}' not found in source.")

    start_line = node.lineno
    if hasattr(node, "decorator_list") and node.decorator_list:
        start_line = min(start_line, node.decorator_list[0].lineno)
    end_line = node.end_lineno

    lines = source.splitlines()
    target_lines = lines[start_line - 1 : end_line]
    return "\n".join(target_lines)


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python3 ast_helpers.py <action> <file_path> [options/args]",
            file=sys.stderr,
        )
        print("Actions: symbols, hash, skeleton, symbol-block", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if action == "symbols":
            symbols = extract_symbols(source)
            print(json.dumps(symbols, indent=2))

        elif action == "hash":
            symbol_name = None
            if "--symbol" in sys.argv:
                idx = sys.argv.index("--symbol")
                if idx + 1 < len(sys.argv):
                    symbol_name = sys.argv[idx + 1]
                else:
                    print("Error: --symbol requires an argument.", file=sys.stderr)
                    sys.exit(1)

            try:
                h = calculate_hash(source, symbol_name)
                rel_path = os.path.relpath(file_path)
                result = {
                    "file": rel_path,
                    "symbol": symbol_name,
                    "hash": h,
                    "algorithm": "sha256",
                }
                print(json.dumps(result, indent=2))
            except ValueError as ve:
                print(f"Error: {ve}", file=sys.stderr)
                sys.exit(1)

        elif action == "skeleton":
            skeleton = generate_skeleton(source)
            print(skeleton)

        elif action == "symbol-block":
            if len(sys.argv) < 4:
                print(
                    "Error: Action 'symbol-block' requires a symbol name.",
                    file=sys.stderr,
                )
                print(
                    "Usage: python3 ast_helpers.py symbol-block <file_path> <symbol_name>",
                    file=sys.stderr,
                )
                sys.exit(1)
            symbol_name = sys.argv[3]
            try:
                block = get_symbol_block(source, symbol_name)
                print(block)
            except ValueError as ve:
                print(f"Error: {ve}", file=sys.stderr)
                sys.exit(1)

        else:
            print(f"Error: Unknown action '{action}'", file=sys.stderr)
            sys.exit(1)

    except SyntaxError as se:
        print(f"Syntax Error parsing file: {se}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
