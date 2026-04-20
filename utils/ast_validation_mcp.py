import os
import ast
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ast_validation_mcp")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _is_safe_path(path: str) -> bool:
    abs_path = os.path.abspath(path)
    return abs_path.startswith(BASE_DIR)

def _read_ast(file_path: str):
    if os.path.isabs(file_path) and file_path.startswith(BASE_DIR):
        file_path = os.path.relpath(file_path, BASE_DIR)
        
    if file_path.startswith(".staging/"):
        file_path = file_path.replace(".staging/", "", 1)
        
    staging_path = os.path.join(BASE_DIR, ".staging", file_path)
    base_path = os.path.join(BASE_DIR, file_path)
    target_path = staging_path if os.path.exists(staging_path) else base_path
    
    if not _is_safe_path(target_path):
        raise Exception(f"[SECURITY ERROR] Path {target_path} escapes workspace bounded box.")
    if not os.path.exists(target_path):
        raise Exception(f"[ERROR] File not found: {file_path}")
        
    with open(target_path, "r", encoding="utf-8") as f:
        source = f.read()
    return ast.parse(source), source

@mcp.tool()
def validate_python_syntax(file_path: str) -> str:
    """Programmatically attempts to compile the Python source into an AST to verify syntax validity."""
    try:
        _read_ast(file_path)
        return f"[SUCCESS] Valid Python syntax in '{file_path}'"
    except SyntaxError as e:
        return f"[SYNTAX ERROR] Could not compile '{file_path}':\nLine {e.lineno}, offset {e.offset}: {e.text.strip() if e.text else ''}\nDetails: {e.msg}"
    except Exception as e:
        return f"[ERROR] {e}"

@mcp.tool()
def extract_python_function(file_path: str, function_name: str) -> str:
    """Parses the Python syntax tree natively and extracts the literal source code block of a specified function or class."""
    try:
        tree, source = _read_ast(file_path)
    except Exception as e:
        return f"[ERROR] {e}"
        
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == function_name:
                return ast.get_source_segment(source, node)
    return f"[ERROR] Construct '{function_name}' not found in {file_path}"

@mcp.tool()
def verify_decorator_exists(file_path: str, target_decorator: str, construct_name: str = "") -> str:
    """Walks the AST to find specific decorators, optionally scoping the query to a specific function/class name."""
    try:
        tree, _ = _read_ast(file_path)
    except Exception as e:
        return f"[ERROR] {e}"
        
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if construct_name and node.name != construct_name:
                continue
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name) and dec.id == target_decorator:
                    return f"[TRUE] Decorator '@{target_decorator}' found on construct '{node.name}'"
                elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and dec.func.id == target_decorator:
                    return f"[TRUE] Decorator '@{target_decorator}(...)' found on construct '{node.name}'"
                
    suffix = f" on '{construct_name}'" if construct_name else ""
    return f"[FALSE] Decorator '{target_decorator}' not found{suffix} in {file_path}"

@mcp.tool()
def verify_import_exists(file_path: str, module_name: str, object_name: str = "") -> str:
    """Sweeps the AST's Import nodes to verify if required modules were properly imported, preventing hallucination loops."""
    try:
        tree, _ = _read_ast(file_path)
    except Exception as e:
        return f"[ERROR] {e}"
        
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == module_name and not object_name:
                    return f"[TRUE] 'import {module_name}' found"
        elif isinstance(node, ast.ImportFrom):
            if node.module == module_name:
                if not object_name:
                    return f"[TRUE] 'from {module_name} import ...' found"
                for alias in node.names:
                    if alias.name == object_name:
                        return f"[TRUE] 'from {module_name} import {object_name}' found"
                        
    search_str = f"from {module_name} import {object_name}" if object_name else f"import {module_name}"
    return f"[FALSE] Required import '{search_str}' not physically found in AST"

@mcp.tool()
def detect_unsafe_functions(file_path: str) -> str:
    """Statically scans the AST for inherently dangerous Python primitives (eval, exec, os.system)."""
    try:
        tree, _ = _read_ast(file_path)
    except Exception as e:
        return f"[ERROR] {e}"
        
    unsafe_calls = ["eval", "exec", "os.system", "subprocess.run", "subprocess.Popen"]
    violations = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_str = ""
            if isinstance(node.func, ast.Name):
                call_str = node.func.id
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    call_str = f"{node.func.value.id}.{node.func.attr}"
            
            if call_str in unsafe_calls:
                violations.append(f"Line {node.lineno}: {call_str}() detected")
                
    if violations:
        return "[SECURITY VIOLATION] Unsafe primitive execution detected:\n" + "\n".join(violations)
    return "[CLEAN] No intrinsically unsafe functions detected in AST."

if __name__ == "__main__":
    mcp.run()
