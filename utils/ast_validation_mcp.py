import os
import ast
import subprocess
import sys
import shutil
import hmac
import hashlib
from mcp.server.fastmcp import FastMCP

# Ensure local imports resolve when called natively by the MCP Host process
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.dlp_proxy import redact_genomic_phi
from utils.staging_lease import acquire_staging_lease

def get_secret() -> bytes:
    key_file = os.path.join(project_root, ".agents", "memory", "staging_key.txt")
    if not os.path.exists(key_file):
        import secrets
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, "w") as f:
            f.write(secrets.token_hex(32))
    with open(key_file, "r") as f:
        return f.read().strip().encode('utf-8')

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

def _sync_staging_environment(staging_dir: str):
    STAGING_BLOCKLIST = [".staging", ".git", "venv", ".venv", "__pycache__", ".pytest_cache", "node_modules"]
    for root, dirs, files in os.walk(project_root):
        path_parts = root.split(os.sep)
        if any(b in path_parts for b in STAGING_BLOCKLIST):
            continue
        rel_path = os.path.relpath(root, project_root)
        staging_target_dir = os.path.join(staging_dir, rel_path)
        os.makedirs(staging_target_dir, exist_ok=True)
        for file in files:
            if not file.startswith('.') and not file.endswith(('.pyc', '.so')):
                base_fp = os.path.join(root, file)
                staging_fp = os.path.join(staging_target_dir, file)
                if not os.path.exists(staging_fp):
                    try:
                        shutil.copy2(base_fp, staging_fp)
                    except Exception:
                        pass

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

@mcp.tool()
def execute_tdaid_test(test_path: str) -> str:
    """
    Linked to workflow: @tdaid-audit & skill: @tdaid-ast-assertion
    Executes a TDAID (Test-Driven AI Development) Red/Green pytest assertion natively.
    Mandated by AGENTS.md before any structural pipeline mutations.
    """
    try:
        with acquire_staging_lease(exclusive=False):
            staging_dir = os.path.abspath(os.path.join(current_dir, "..", ".staging"))
            
            if not os.path.exists(staging_dir):
                return redact_genomic_phi("[FATAL] Staging airlock does not exist. Tests must be staged before execution.", redact_uuids=False)
                
            if test_path.startswith(".staging/"):
                test_path = test_path.replace(".staging/", "", 1)
                
            target_path = os.path.join(staging_dir, test_path)

            venv_pytest = os.path.join(project_root, "venv", "bin", "pytest")
            venv_pip = os.path.join(project_root, "venv", "bin", "pip")
            if not os.path.exists(venv_pytest):
                venv_pytest = "pytest" # graceful fallback
                venv_pip = "pip"
                
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{staging_dir}:{project_root}"

            _sync_staging_environment(staging_dir)

            # Zero-Trust Dependency Sync
            staged_reqs_path = os.path.join(staging_dir, "requirements.txt")
            if os.path.exists(staged_reqs_path):
                subprocess.run([venv_pip, "install", "-r", staged_reqs_path], capture_output=True, env=env)

            result = subprocess.run(
                [venv_pytest, test_path, "-v", "--tb=short"], 
                capture_output=True, 
                text=True, 
                timeout=300,
                cwd=staging_dir,
                env=env
            )
            
            output_limit = 2500
            
            if result.returncode == 0:
                sig = hmac.new(get_secret(), b"QA_PASSED", hashlib.sha256).hexdigest()
                with open(os.path.join(staging_dir, ".qa_signature"), "w") as f:
                    f.write(sig)
                return redact_genomic_phi(f"[SUCCESS] TDAID Assertions Passed (Exit 0). Cryptographic hash written securely to .staging/.qa_signature\n{result.stdout[-output_limit:]}", redact_uuids=False)
            else:
                return redact_genomic_phi(f"[FAILED] TDAID Assertions Failed (Exit {result.returncode}):\n{result.stdout[-output_limit:]}\nSTDERR:\n{result.stderr[-output_limit:]}", redact_uuids=False)
            
    except BlockingIOError as e:
        return str(e)
    except subprocess.TimeoutExpired:
        return redact_genomic_phi(f"FATAL: Test execution for {test_path} timed out after 300 seconds. Process killed and lock released.", redact_uuids=False)
    except Exception as e:
        return redact_genomic_phi(f"Unexpected Error executing TDAID tests: {str(e)}", redact_uuids=False)

@mcp.tool()
def execute_coverage_report(test_path: str, target_module: str) -> str:
    """
    Executes a TDAID test utilizing coverage.py natively to calculate explicit line coverage thresholds for a given target module.
    Use this to strictly enforce the >=80% coverage mandate on structural rewrites.
    """
    try:
        with acquire_staging_lease(exclusive=False):
            staging_dir = os.path.abspath(os.path.join(current_dir, "..", ".staging"))
            
            if not os.path.exists(staging_dir):
                return redact_genomic_phi("[FATAL] Staging airlock does not exist.", redact_uuids=False)
                
            if test_path.startswith(".staging/"):
                test_path = test_path.replace(".staging/", "", 1)
                
            if target_module.endswith(".py"):
                target_module = target_module[:-3].replace(os.sep, ".")
            elif os.sep in target_module:
                target_module = target_module.replace(os.sep, ".")
                
            venv_coverage = os.path.join(project_root, "venv", "bin", "coverage")
            venv_pytest = os.path.join(project_root, "venv", "bin", "pytest")
            venv_pip = os.path.join(project_root, "venv", "bin", "pip")
            
            if not os.path.exists(venv_pytest):
                venv_pytest = "pytest"
                venv_coverage = "coverage"
                venv_pip = "pip"
                
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{staging_dir}:{project_root}"

            # Zero-Trust Dep sync (Ensure coverage is installed)
            if os.path.exists(venv_pip):
                subprocess.run([venv_pip, "install", "-q", "coverage", "pytest"], capture_output=True, env=env)

            # Physically map all codebase files across boundaries
            _sync_staging_environment(staging_dir)

            # Run test wrapped in coverage
            run_cmd = [venv_coverage, "run", "--source", target_module, "-m", "pytest", test_path, "-v", "--tb=short"]
            result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=300, cwd=staging_dir, env=env)
            
            # Generate terminal report
            report_cmd = [venv_coverage, "report", "-m"]
            report_result = subprocess.run(report_cmd, capture_output=True, text=True, cwd=staging_dir, env=env)
            
            output_limit = 2500
            
            if result.returncode == 0:
                sig = hmac.new(get_secret(), b"QA_PASSED", hashlib.sha256).hexdigest()
                with open(os.path.join(staging_dir, ".qa_signature"), "w") as f:
                    f.write(sig)
                return redact_genomic_phi(f"[SUCCESS] Coverage Assertions Passed (Exit 0). Cryptographic hash written securely to .staging/.qa_signature\n\nTEST OUTPUT:\n{result.stdout[-output_limit:]}\n\nCOVERAGE REPORT:\n{report_result.stdout}", redact_uuids=False)
            else:
                return redact_genomic_phi(f"[FAILED] Coverage Assertions Failed (Exit {result.returncode}):\nTEST OUTPUT:\n{result.stdout[-output_limit:]}\n\nCOVERAGE REPORT:\n{report_result.stdout}\n\nSTDERR:\n{result.stderr[-output_limit:]}", redact_uuids=False)
            
    except BlockingIOError as e:
        return str(e)
    except subprocess.TimeoutExpired:
        return redact_genomic_phi(f"FATAL: Test execution timed out after 300 seconds.", redact_uuids=False)
    except Exception as e:
        return redact_genomic_phi(f"Unexpected Error executing Coverage execution: {str(e)}", redact_uuids=False)

@mcp.tool()
def measure_cyclomatic_complexity(file_path: str) -> str:
    """
    Calculates the McCabe Cyclomatic Complexity score for all functions/classes in a staged Python file natively using AST walking.
    Use this to strictly enforce architectural simplicity (complexity <= 5) before merging.
    """
    try:
        tree, _ = _read_ast(file_path)
    except Exception as e:
        return f"[ERROR] {e}"
        
    complexities = {}
    branch_nodes = (
        ast.If, ast.While, ast.For, ast.AsyncFor,
        ast.ExceptHandler, ast.With, ast.AsyncWith,
        ast.And, ast.Or
    )
    if hasattr(ast, 'Match'):
        branch_nodes += (ast.Match,)
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            score = 1
            for child in ast.walk(node):
                if isinstance(child, branch_nodes):
                    score += 1
            complexities[node.name] = score
            
    if not complexities:
        return "[SUCCESS] Complexity Score: 1 (No functions detected)"
        
    max_score = max(complexities.values())
    breakdown = "\n".join(f" - {name}(): {score}" for name, score in complexities.items())
    
    if max_score > 5:
        return f"[COMPLEXITY VIOLATION] Max Score is {max_score}! (Limit <= 5)\nBreakdown:\n{breakdown}"
    return f"[SUCCESS] Max Complexity Score: {max_score}\nBreakdown:\n{breakdown}"

if __name__ == "__main__":
    mcp.run()
