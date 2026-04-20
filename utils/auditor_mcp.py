import os
import shutil
import sys
from mcp.server.fastmcp import FastMCP

# Ensure local imports resolve when called natively by the MCP Host process
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.dlp_proxy import redact_genomic_phi
from utils.staging_lease import acquire_staging_lease
import hmac
import hashlib

def get_secret() -> bytes:
    return b"NGS_ZERO_TRUST_SIMULATION_KEY_2026"

mcp = FastMCP("Auditor Validation Server")

def _is_safe_path(path: str) -> bool:
    abs_path = os.path.abspath(path)
    return abs_path.startswith(project_root)

@mcp.tool()
def read_workspace_file(file_path: str) -> str:
    """Reads a file natively. Evaluates the `.staging` airlock first, falling back to the main workspace."""
    if os.path.isabs(file_path) and file_path.startswith(project_root):
        file_path = os.path.relpath(file_path, project_root)
        
    if file_path.startswith(".staging/"):
        file_path = file_path.replace(".staging/", "", 1)
        
    staging_path = os.path.join(project_root, ".staging", file_path)
    base_path = os.path.join(project_root, file_path)
    
    target_path = staging_path if os.path.exists(staging_path) else base_path

    if not _is_safe_path(target_path):
        return f"[SECURITY ERROR] Path {target_path} escapes workspace bounded box."
    if not os.path.exists(target_path):
        return f"[ERROR] File not found: {file_path}"
        
    with open(target_path, "r") as f:
        return f.read()


@mcp.tool()
def promote_staging_area() -> str:
    """
    Linked to workflow: @tdaid-audit.
    Natively merges all mutated `.staging/` scripts back into the main repository.
    The Auditor MUST ONLY execute this natively if the architectural critique passes and TDAID tests exited 0.
    """
    staging_dir = os.path.abspath(os.path.join(project_root, ".staging"))
    sig_file = os.path.join(staging_dir, ".qa_signature")
    
    if not os.path.exists(staging_dir):
        return redact_genomic_phi("[FATAL] Staging area does not exist. Nothing to promote.", redact_uuids=False)
        
    try:
        with acquire_staging_lease(exclusive=True):
            # 1. Physical Cryptographic Authentication Gate
            if not os.path.exists(sig_file):
                return redact_genomic_phi("[SECURITY FATAL] Cryptographic token missing. The Executor hallucinated the TDAID assertion. Promotion physically blocked.", redact_uuids=False)
                
            with open(sig_file, "r") as f:
                sig = f.read().strip()
                
            expected_sig = hmac.new(get_secret(), b"QA_PASSED", hashlib.sha256).hexdigest()
            if sig != expected_sig:
                return redact_genomic_phi("[SECURITY FATAL] Cryptographic HMAC mismatch! Staging area compromised. Promotion blocked.", redact_uuids=False)
                
            # 2. Host OS Modification (Strict Zero-Trust Directory Whitelist mapped to rsync)
            import subprocess
            
            # Explicitly hardcode the exact structural branches the Swarm is authorized to mutate
            approved_dirs = [
                "api", "agent_app", "orchestrator", "infrastructure", 
                "utils", "tests", "core", "src", "etl", "db-init", 
                "alembic", "bin", "docker"
            ]
            
            for directory in approved_dirs:
                source_path = os.path.join(staging_dir, directory)
                if os.path.exists(source_path):
                    # Enforce exact synchronization using native OS binaries, protecting node_modules/venv
                    subprocess.run([
                        "rsync", "-av", "--no-links",
                        "--exclude", "__pycache__", 
                        "--exclude", ".pytest_cache", 
                        "--exclude", "*.pyc",
                        f"{source_path}/", f"{project_root}/{directory}/"
                    ], check=True, capture_output=True, text=True)
            
            shutil.rmtree(staging_dir)
            return redact_genomic_phi("[SUCCESS] Staging area gracefully integrated into Production Codebase.", redact_uuids=False)
            
    except BlockingIOError as e:
        return str(e)
    except Exception as e:
        return redact_genomic_phi(f"[ERROR] Promotion Failure: {str(e)}", redact_uuids=False)

@mcp.tool()
def teardown_staging_area() -> str:
    """
    Linked to workflow: @staging-promotion fallback.
    Forcefully purges the `.staging/` buffer. Essential for resetting the environment 
    when testing loops are aborted or architectural violations occur.
    """
    staging_dir = os.path.abspath(os.path.join(project_root, ".staging"))
    
    if not os.path.exists(staging_dir):
        return redact_genomic_phi("[INFO] Staging area does not exist. No teardown required.", redact_uuids=False)
        
    try:
        with acquire_staging_lease(exclusive=True):
            shutil.rmtree(staging_dir)
            return redact_genomic_phi("[SUCCESS] Staging area successfully purged.", redact_uuids=False)
    except BlockingIOError as e:
        return str(e)
    except Exception as e:
        return redact_genomic_phi(f"[ERROR] Teardown Failure: {str(e)}", redact_uuids=False)

if __name__ == "__main__":
    mcp.run()
