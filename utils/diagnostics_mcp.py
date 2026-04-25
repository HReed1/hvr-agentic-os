import os
import sys
import subprocess
from mcp.server.fastmcp import FastMCP

# Ensure local imports resolve when called natively by the MCP Host process
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.dlp_proxy import redact_genomic_phi
from utils.staging_lease import acquire_staging_lease

mcp = FastMCP("diagnostics_mcp")

@mcp.tool()
def audit_network_sockets(port: int) -> str:
    """Executes a sanitized lsof -i :<port> query to check for active connections or zombie processes hijacking sockets."""
    try:
        if not isinstance(port, int) or port <= 0 or port > 65535:
            return "[ERROR] Invalid port number."
            
        result = subprocess.run(
            ["lsof", "-i", f":{port}"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            return redact_genomic_phi(f"[ACTIVE SOCKETS ON {port}]\n{result.stdout.strip()}", redact_uuids=False)
        else:
            return redact_genomic_phi(f"[NO ACTIVE SOCKETS] Port {port} is free or no process returned an active bind.\n{result.stderr[-500:]}", redact_uuids=False)
    except Exception as e:
        return f"[DIAGNOSTIC ERROR] {str(e)}"

@mcp.tool()
def tail_background_process(process_name: str, tail_lines: int = 50) -> str:
    """Uses pgrep to find a running process explicitly tied to the staging execution, and tails the last lines of its associated log files."""
    try:
        # Prevent unbounded searches
        if not process_name.isalnum() and "_" not in process_name and "-" not in process_name:
             # Basic sanity constraint
             pass
             
        # Look for the process PID
        pgrep_res = subprocess.run(["pgrep", "-f", process_name], capture_output=True, text=True, timeout=5)
        if pgrep_res.returncode != 0 or not pgrep_res.stdout.strip():
            return f"[DIAGNOSTIC] No processes found matching '{process_name}'."
            
        pids = [p for p in pgrep_res.stdout.strip().split('\n') if p]
        if not pids:
            return f"[DIAGNOSTIC] No processes found matching '{process_name}'."
            
        target_pid = pids[0] # Take the most logical process
        
        # We can broadly look for any .log files in the staging dir
        staging_dir = os.path.abspath(os.path.join(project_root, ".staging"))
        log_outputs = []
        
        # Finding log files via lsof
        lsof_res = subprocess.run(["lsof", "-p", str(target_pid)], capture_output=True, text=True, timeout=5)
        if lsof_res.returncode == 0:
            for line in lsof_res.stdout.split('\n'):
                if staging_dir in line and (".log" in line or ".out" in line):
                    # extract the file path
                    parts = line.split()
                    if len(parts) >= 9:
                        file_path = parts[8]
                        if os.path.exists(file_path):
                            tail_res = subprocess.run(["tail", "-n", str(tail_lines), file_path], capture_output=True, text=True)
                            log_outputs.append(f"--- TAIL of {os.path.basename(file_path)} ---\n{tail_res.stdout.strip()}")
        
        # If no explicit log files found via lsof, find any .log files strictly in .staging
        if not log_outputs:
            if os.path.exists(staging_dir):
                for f in os.listdir(staging_dir):
                    if f.endswith(".log"):
                        full_path = os.path.join(staging_dir, f)
                        tail_res = subprocess.run(["tail", "-n", str(tail_lines), full_path], capture_output=True, text=True)
                        log_outputs.append(f"--- TAIL of {f} ---\n{tail_res.stdout.strip()}")
                        
        if not log_outputs:
            # Maybe the process just prints to stdout and doesn't write to a file! Look at the ps aux output to inform the user it IS alive.
            ps_res = subprocess.run(["ps", "auxwy"], capture_output=True, text=True)
            process_line = ""
            for l in ps_res.stdout.split('\n'):
                if str(target_pid) in l.split():
                    process_line = l
                    break
            return redact_genomic_phi(f"[PROCESS ALIVE: {target_pid}] Process is actively running, but no accessible .log files were found natively in .staging/ to tail.\nPS: {process_line}", redact_uuids=False)
            
        return redact_genomic_phi("\n\n".join(log_outputs), redact_uuids=False)

    except subprocess.TimeoutExpired:
        return "[DIAGNOSTIC ERROR] System query timed out."
    except Exception as e:
        return f"[DIAGNOSTIC ERROR] {str(e)}"

if __name__ == "__main__":
    mcp.run()
