import sys
import os
import subprocess
from mcp.server.fastmcp import FastMCP

# Ensure local imports resolve
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.dlp_proxy import redact_genomic_phi

mcp = FastMCP("Repository Wrapup Telemetry")

def run_helper_script(script_name: str, use_bash: bool = False, *args) -> str:
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
        
        command = ["bash", script_path] if use_bash else ["python3", script_path]
        command.extend(list(args))
        
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        if result.returncode == 0:
            return redact_genomic_phi(result.stdout, redact_uuids=False)
        else:
            return redact_genomic_phi(f"Tool Failed ({result.returncode}):\n{result.stderr}\n{result.stdout}", redact_uuids=False)
    except subprocess.TimeoutExpired:
        return redact_genomic_phi(f"FATAL: Execution exceeded 60-second timeout for {script_name}.", redact_uuids=False)
    except Exception as e:
        return redact_genomic_phi(f"Unexpected invocation error: {str(e)}", redact_uuids=False)


@mcp.tool()
def run_timestamp_prefixing() -> str:
    """
    Linked to workflow: @executor-wrapup
    Natively executes the bash timeline-prefixer to lock local artifacts with OS chronologies.
    """
    return run_helper_script("timestamp_docs.sh", use_bash=True)

@mcp.tool()
def run_doc_link_sync() -> str:
    """
    Linked to workflow: @executor-wrapup
    Synchronously updates local markdown path relationships to adapt to recently prepended timestamps.
    """
    return run_helper_script("refactor_doc_links.py")

if __name__ == "__main__":
    mcp.run()
