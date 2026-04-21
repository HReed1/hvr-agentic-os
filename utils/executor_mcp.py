import os
import subprocess
import shutil
from mcp.server.fastmcp import FastMCP

CONTEXT_SAFE_MODE = os.environ.get("ADK_CONTEXT_SAFE_MODE", "false").lower() == "true"

mcp = FastMCP("executor_mcp")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _is_safe_path(path: str) -> bool:
    """Ensures the absolute path resolves inside the active workspace."""
    abs_path = os.path.abspath(path)
    return abs_path.startswith(BASE_DIR)

STAGING_BLOCKLIST = [".staging", ".git", "venv", ".venv", "__pycache__", ".pytest_cache", "node_modules"]

def _resolve_airlock_path(file_path: str) -> tuple[str, str, str]:
    if os.path.isabs(file_path) and file_path.startswith(BASE_DIR):
        file_path = os.path.relpath(file_path, BASE_DIR)
    if file_path.startswith(".staging/"):
        file_path = file_path.replace(".staging/", "", 1)
        
    staging_path = os.path.join(BASE_DIR, ".staging", file_path)
    base_path = os.path.join(BASE_DIR, file_path)
    return file_path, staging_path, base_path

def _ensure_staged():
    """Lazily populates the .staging airlock with physical copies of the workspace if unprimed."""
    staging_dir = os.path.join(BASE_DIR, ".staging")
    os.makedirs(staging_dir, exist_ok=True)
    flag_file = os.path.join(staging_dir, ".primed")
    
    if os.path.exists(flag_file):
        return
        
    for root, dirs, files in os.walk(BASE_DIR):
        if any(b in os.path.join(root, "") for b in [f"/{x}/" for x in STAGING_BLOCKLIST] + [f"\\{x}\\" for x in STAGING_BLOCKLIST] + [f"/{x}" for x in STAGING_BLOCKLIST] + [f"{x}/" for x in STAGING_BLOCKLIST]):
            # Quick substring matching for blocklist dirs
            continue
            
        # A more robust check for blocklist elements in path parts
        path_parts = root.split(os.sep)
        if any(b in path_parts for b in STAGING_BLOCKLIST):
            continue
            
        rel_path = os.path.relpath(root, BASE_DIR)
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
                        
    with open(flag_file, "w") as f:
        f.write("primed")

@mcp.tool()
def read_workspace_file(file_path: str) -> str:
    """Reads a file natively. Evaluates the `.staging` airlock first, falling back to the main workspace."""
    _ensure_staged()
    file_path, staging_path, base_path = _resolve_airlock_path(file_path)
    
    # Evaluate airlock first
    target_path = staging_path if os.path.exists(staging_path) else base_path

    if not _is_safe_path(target_path):
        return f"[SECURITY ERROR] Path {target_path} escapes workspace bounded box."
    if not os.path.exists(target_path):
        return f"[ERROR] File not found: {file_path}"
        
    with open(target_path, "r") as f:
        lines = f.readlines()
        
        limit = 8000 if CONTEXT_SAFE_MODE else 50000
        content_length = sum(len(l) for l in lines)
        if content_length > limit:
            return f"[ERROR] File is too large ({content_length} bytes). Use 'search_workspace' to preserve LLM token budgets."
            
        numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
        return "".join(numbered_lines)

@mcp.tool()
def list_workspace_directory(directory_path: str = ".") -> str:
    """Lists the contents of a directory. Physically trapped inside the `.staging` airlock or base workspace."""
    _ensure_staged()
    directory_path, staging_path, base_path = _resolve_airlock_path(directory_path)
    
    if not _is_safe_path(base_path):
        return f"[SECURITY ERROR] Path escapes workspace bounds."
        
    items = set()
    try:
        if os.path.exists(base_path) and os.path.isdir(base_path):
            items.update(os.listdir(base_path))
    except Exception:
        pass

    try:
        if os.path.exists(staging_path) and os.path.isdir(staging_path):
            items.update(os.listdir(staging_path))
    except Exception:
        pass
        
    # Filter out .staging to prevent recursive confusion
    if ".staging" in items:
        items.remove(".staging")
        
    if not items:
        return f"[ERROR] Directory not found or empty: {directory_path}"
        
    return "\n".join(sorted(list(items)))
    
@mcp.tool()
def _build_search_index(base_path, staging_path):
    files_to_search = {}
    
    if os.path.exists(base_path):
        if os.path.isfile(base_path):
            files_to_search[os.path.relpath(base_path, BASE_DIR)] = base_path
        else:
            for root, _, files in os.walk(base_path):
                if '.git' in root or '.staging' in root or 'venv' in root or '__pycache__' in root:
                    continue
                for f in files:
                    if not f.startswith('.') and not f.endswith(('.pyc', '.so')):
                        full_path = os.path.join(root, f)
                        files_to_search[os.path.relpath(full_path, BASE_DIR)] = full_path
                        
    if os.path.exists(staging_path):
        if os.path.isfile(staging_path):
            rel = os.path.relpath(staging_path, BASE_DIR).replace(".staging/", "", 1)
            files_to_search[rel] = staging_path
        else:
            for root, _, files in os.walk(staging_path):
                for f in files:
                    if not f.startswith('.') and not f.endswith('.pyc'):
                        full_path = os.path.join(root, f)
                        rel = os.path.relpath(full_path, BASE_DIR).replace(".staging/", "", 1)
                        files_to_search[rel] = full_path
                        
    return files_to_search

@mcp.tool()
def search_workspace(query: str, directory_path: str = ".") -> str:
    """Searches for a text query inside files natively. Trapped inside the `.staging` airlock."""
    _ensure_staged()
    directory_path, staging_path, base_path = _resolve_airlock_path(directory_path)
    
    if not _is_safe_path(base_path):
        return f"[SECURITY ERROR] Path escapes workspace bounds."
        
    try:
        results = []
        files_to_search = _build_search_index(base_path, staging_path)
        
        for rel_path, file_path in files_to_search.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if query in line:
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            results.append(f"--- {rel_path} (Context L{start+1}-L{end}) ---")
                            for j in range(start, end):
                                marker = ">>" if j == i else "  "
                                results.append(f"{j+1} {marker} {lines[j].rstrip()}")
                            results.append("")
                            if sum(1 for r in results if "---" in r) >= 25:
                                return "\n".join(results) + "\n[WARNING: MAX RESULTS TRUNCATED]"
            except UnicodeDecodeError:
                pass
        return "\n".join(results) if results else f"[NO MATCHES FOUND FOR '{query}']"
    except Exception as e:
        return f"[ERROR] Exception searching workspace: {e}"

@mcp.tool()
def write_workspace_file(file_path: str, content: str, overwrite: bool = False) -> str:
    """Writes/mutates a file natively. Physically trapped inside the `.staging` airlock."""
    _ensure_staged()
    file_path, target_path, base_path = _resolve_airlock_path(file_path)

    if not _is_safe_path(target_path):
        return f"[SECURITY ERROR] Path {target_path} escapes workspace bounded box."
        
    if os.path.exists(target_path) or os.path.exists(base_path):
        # Prevent lazy full-file overwrites on existing codebase files unless explicitly flagged
        if not file_path.startswith("tests/") and not overwrite:
            return f"[ERROR] Lazy overwrites disabled. You must use `replace_workspace_file_content` OR explicitly invoke `write_workspace_file` with the parameter `overwrite=true`."

    if "\\n" in content and "\n" not in content:
        content = content.replace("\\n", "\n")
        
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w") as f:
        f.write(content)
    return f"[SUCCESS] Staged mutation in airlock: .staging/{file_path}"

@mcp.tool()
def replace_workspace_file_content(file_path: str, replacement_string: str, start_line: int, end_line: int) -> str:
    """Surgically replaces a block of lines within a file using deterministic index bounds. Physically trapped inside `.staging`."""
    _ensure_staged()
    file_path, target_path, base_path = _resolve_airlock_path(file_path)

    if not _is_safe_path(target_path):
        return f"[SECURITY ERROR] Path {target_path} escapes workspace bounded box."
        
    if not os.path.exists(target_path):
        if os.path.exists(base_path):
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(base_path, target_path)
        else:
            return f"[ERROR] Target file does not exist: {file_path}"
    
    with open(target_path, "r") as f:
        lines = f.readlines()
        
    if not (1 <= start_line <= len(lines) and start_line <= end_line <= len(lines)):
        return f"[ERROR] Invalid line range. The file '{file_path}' has {len(lines)} lines. Ensure start_line <= end_line and bounds are correct."
        
    prefix = "".join(lines[:start_line-1])
    suffix = "".join(lines[end_line:])
    
    # Safely inject the new replacement block
    rep = replacement_string
    if "\\n" in rep and "\n" not in rep:
        rep = rep.replace("\\n", "\n")
        
    if rep and not rep.endswith("\n"):
        rep += "\n"
        
    new_content = prefix + rep + suffix
        
    with open(target_path, "w") as f:
        f.write(new_content)
    return f"[SUCCESS] Staged surgical mutation (Lines {start_line}-{end_line}) in airlock: .staging/{file_path}"

@mcp.tool()
def append_workspace_file_content(file_path: str, content: str) -> str:
    """Appends content to the end of a file. Physically trapped inside the `.staging` airlock."""
    _ensure_staged()
    file_path, target_path, base_path = _resolve_airlock_path(file_path)

    if not _is_safe_path(target_path):
        return f"[SECURITY ERROR] Path {target_path} escapes workspace bounded box."
        
    if not os.path.exists(target_path):
        if os.path.exists(base_path):
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(base_path, target_path)
        else:
            return f"[ERROR] Target file does not exist to append to: {file_path}"
            
    with open(target_path, "a") as f:
        f.write("\n" + content)
    return f"[SUCCESS] Staged appending mutation in airlock: .staging/{file_path}"

@mcp.tool()
def execute_transient_docker_sandbox(command: str, image: str = "executor-sandbox:latest") -> str:
    """
    Escapes native execution via a throwaway Docker container mounted strictly to the `.staging` airlock.
    Requires explicitly delegated authority from the Architect.
    """
    staging_dir = os.path.join(BASE_DIR, ".staging")
    if not os.path.exists(staging_dir):
        os.makedirs(staging_dir, exist_ok=True)
    
    # Automatically pull core logic branches and the dependency manifest into the sandbox cleanly
    for target in ["src", "utils", "agent_app", "api", "tests", "core", "requirements.txt", "etl", "mcp_host_layer", ".agents", "docs", "infrastructure"]:
        src = os.path.join(BASE_DIR, target)
        dst = os.path.join(staging_dir, target)
        if os.path.exists(src):
            try:
                if os.path.isdir(src):
                    import shutil
                    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("node_modules", "__pycache__", ".pytest_cache", "venv", ".venv"))
                else:
                    import shutil
                    shutil.copy2(src, dst)
            except Exception:
                # Ignore SameFileErrors and sync collisions if the airlock is already mapped
                pass

    import shutil
    # Headless environments (like adk eval) may strip /usr/local/bin from PATH. Fallback explicitly.
    docker_bin = shutil.which("docker") or "/usr/local/bin/docker"
    if not os.path.exists(docker_bin):
        docker_bin = "/opt/homebrew/bin/docker"

    # Uses the configured image (defaulting to executor-sandbox) allocating file-descriptor links securely
    docker_cmd = [
        docker_bin, "run", "--rm",
        "--add-host=host.docker.internal:host-gateway",
        "-e", "DB_HOST=host.docker.internal",
        "-v", f"{staging_dir}:/workspace",
        "-w", "/workspace",
        image,
        "sh", "-c",
        command
    ]
    
    try:
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout if result.returncode == 0 else f"[ERROR] {result.stderr}\n{result.stdout}"
    except subprocess.TimeoutExpired:
        return "[ERROR] Sandbox execution timed out exceeding FinOps limits."
    except FileNotFoundError:
         return "[ERROR] Docker engine is not running on the local host."

@mcp.tool()
def inspect_container_os_release(image_uri: str) -> str:
    """
    Safely inspects the OS distribution and primary package managers inside a target container.
    Physically stripped of network footprinting and bash shell hijacking.
    """
    # Force single-argument validation, preventing malicious command injection 
    if ";" in image_uri or "&" in image_uri or "|" in image_uri or "$" in image_uri:
        return "[SECURITY FATAL] Bash operator injection detected in image_uri."

    docker_cmd = [
        "docker", "run", "--rm", "--network", "none",
        "--entrypoint", "sh",
        image_uri,
        "-c", "cat /etc/os-release 2>/dev/null; echo '---'; command -v apt-get apk yum 2>/dev/null"
    ]
    
    try:
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return f"[SUCCESS] Container footprint payload:\n{result.stdout.strip()}"
        else:
            return f"[DISTROLESS] Execution failed indicating a distroless or scratched container image:\n{result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "[ERROR] API timeout evaluating container registry."
    except Exception as e:
        return f"[ERROR] Unexpected structural failure pulling {image_uri}: {e}"

if __name__ == "__main__":
    _ensure_staged()
    mcp.run()
