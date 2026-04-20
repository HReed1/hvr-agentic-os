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

mcp = FastMCP("FinOps and Infrastructure Oracle")

def run_helper_script(script_name: str, *args) -> str:
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
        result = subprocess.run(
            [sys.executable, script_path] + list(args), 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        if result.returncode == 0:
            return redact_genomic_phi(result.stdout, redact_uuids=False)
        else:
            return redact_genomic_phi(f"FinOps Tool Failed ({result.returncode}):\n{result.stderr}\n{result.stdout}", redact_uuids=False)
    except subprocess.TimeoutExpired:
        return redact_genomic_phi(f"FATAL: Execution exceeded 60-second timeout for {script_name}.", redact_uuids=False)
    except Exception as e:
        return redact_genomic_phi(f"Unexpected invocation error: {str(e)}", redact_uuids=False)

@mcp.tool()
def estimate_pipeline_cost(run_id: str) -> str:
    """
    Linked to skill: @finops-pricing-oracle
    Evaluates the theoretical or actual AWS Spot / On-Demand cost footprint 
    for a given pipeline Run ID. Use this proactively before architecture changes.
    """
    return run_helper_script("pr_cost_estimator.py", "--run", run_id)

@mcp.tool()
def get_live_job_cost(job_id: str) -> str:
    """
    Linked to skill: @finops-pricing-oracle
    Queries actual per-second EC2 hardware provisioning costs linked 
    to a currently running or recently stopped AWS Batch Job ID natively.
    """
    return run_helper_script("live_job_cost.py", job_id)

@mcp.tool()
def measure_s3_blast(target_path: str) -> str:
    """
    Linked to skill: @finops-s3-sanitation
    REQUIRED READ-ONLY FINOPS GATE: Evaluates the literal S3 physical footprint 
    (size and object count) of the targeted path. Mimicking a deletion payload 
    without mutating anything natively by explicitly forcing structural dry-runs.
    
    Returns explicit sizes the Architect must evaluate before securely requesting
    the User manually approve physical deletion scripts via the Chat GUI.
    """
    return run_helper_script("clean_failed_workdirs.py", target_path, "--dry-run")

@mcp.tool()
def trigger_s3_sanitation(target_path: str, dry_run: bool = True) -> str:
    """
    Linked to skill: @finops-s3-sanitation
    Actively executes the S3 Sanatation payload. By default runs safely as a 
    dry-run. Set dry_run=False ONLY if explicitly approved by the human Director
    to physically delete the objects.
    """
    args = [target_path]
    if dry_run:
        args.append("--dry-run")
    else:
        args.append("--execute")
        
    return run_helper_script("clean_failed_workdirs.py", *args)

@mcp.tool()
def assess_infra_vulns(target_container: str) -> str:
    """
    Linked to skill: @trivy-vuln-sweeper
    Executes a read-only Trivy Vulnerability sweep on the targeted container image.
    Parses the returning JSON directly to prevent LLM shell escaping on CVE arrays.
    """
    return run_helper_script("trivy_vuln_sweeper.sh", target_container)

@mcp.tool()
def assert_postgres_telemetry(run_id: str) -> str:
    """
    Linked to workflow: @architectural-audit
    Queries the database natively via psql using local DB credentials to explicitly 
    assert if a Nextflow orchestrator DAG correctly populated the frontend_runs view.
    """
    import subprocess
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    db_user = os.environ.get("DB_USER", "postgres")
    db_pass = os.environ.get("DB_PASSWORD", "postgres")
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "pipeline_db")
    
    # Secure Postgres environment binding for psql
    env = os.environ.copy()
    env["PGPASSWORD"] = db_pass
    
    query = f"SELECT run_id, dag_step FROM frontend_runs WHERE run_id = '{run_id}';"
    
    try:
        result = subprocess.run(
            ["psql", "-h", db_host, "-p", db_port, "-U", db_user, "-d", db_name, "-c", query],
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            if "0 rows" in result.stdout or "run_id" not in result.stdout:
                return f"[DB ASSERT FAILED] Postgres did not find run_id '{run_id}' in frontend_runs."
            return f"[DB ASSERT SUCCESS] Postgres Output:\n{result.stdout}"
        else:
            return f"[DB ERROR] Psql query failed: {result.stderr}"
    except FileNotFoundError:
        return "[FATAL] `psql` binary is not installed in this environment. Cannot assert DB state."
    except Exception as e:
        return f"[ERROR] Database validation crashed: {str(e)}"

if __name__ == "__main__":
    mcp.run()
