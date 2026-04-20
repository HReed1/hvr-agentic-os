import sys
import os
import boto3
import subprocess
from botocore.exceptions import ClientError
from mcp.server.fastmcp import FastMCP

# Ensure local imports resolve
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.dlp_proxy import redact_genomic_phi

# Initialize FastMCP Server
mcp = FastMCP("AWS Batch Diagnostics Server")

def get_boto3_client(service_name: str):
    """
    Initialize a read-only boto3 client gracefully falling back to the 'admin' profile 
    if standard AWS credentials are not present in the hierarchical execution environment.
    """
    region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    try:
        # Standard environment fallback mapping
        session = boto3.Session()
        if not session.get_credentials():
            # Strict fallback mapping to 'admin' profile per project conventions
            session = boto3.Session(profile_name='admin', region_name=region)
    except Exception:
        session = boto3.Session(profile_name='admin', region_name=region)
        
    return session.client(service_name, region_name=region)

@mcp.tool()
def list_failed_jobs(job_queue: str) -> str:
    """
    Linked to workflow: @aws-triage
    Queries AWS Batch for jobs in the FAILED state for a given compute queue.
    Returns the Job ID, Job Name, and Status Reason format.
    """
    batch_client = get_boto3_client('batch')
    try:
        response = batch_client.list_jobs(
            jobQueue=job_queue,
            jobStatus='FAILED',
            maxResults=50
        )
        jobs = response.get('jobSummaryList', [])
        if not jobs:
            return f"No FAILED jobs located sequentially in queue: {job_queue}"
            
        output = [f"Found {len(jobs)} FAILED Jobs in {job_queue}:"]
        for job in jobs:
            output.append(f"- ID: {job.get('jobId')} | Name: {job.get('jobName')} | Reason: {job.get('statusReason', 'Unknown')}")
            
        return redact_genomic_phi("\n".join(output), redact_uuids=False)
    except ClientError as e:
        return redact_genomic_phi(f"AWS Batch ClientError: {str(e)}", redact_uuids=False)

@mcp.tool()
def describe_batch_job(job_id: str) -> str:
    """
    Linked to workflow: @aws-triage
    Queries AWS Batch to extract deep telemetry for a specific Job ID.
    Returns the explicitly mapped exitCode, statusReason, and CloudWatch logStreamName.
    """
    batch_client = get_boto3_client('batch')
    try:
        response = batch_client.describe_jobs(jobs=[job_id])
        jobs = response.get('jobs', [])
        if not jobs:
            return f"Job ID {job_id} not natively found."
            
        job = jobs[0]
        container = job.get('container', {})
        
        status = job.get('status')
        reason = job.get('statusReason', 'N/A')
        exit_code = container.get('exitCode', 'N/A')
        log_stream = container.get('logStreamName', 'N/A')
        
        return redact_genomic_phi(
            f"Job ID: {job_id}\n"
            f"Status: {status}\n"
            f"Exit Code: {exit_code}\n"
            f"Status Reason: {reason}\n"
            f"Log Stream Name: {log_stream}",
            redact_uuids=False
        )
    except ClientError as e:
        return redact_genomic_phi(f"AWS Batch ClientError: {str(e)}", redact_uuids=False)

@mcp.tool()
def get_job_logs(log_stream_name: str) -> str:
    """
    Linked to workflow: @aws-triage
    Queries AWS CloudWatch Logs matching the /aws/batch/job log group natively.
    Returns the last 100 chronological standard output/error traceback events.
    """
    logs_client = get_boto3_client('logs')
    # Default AWS Batch Execution mapping
    log_group_name = '/aws/batch/job'
    
    try:
        response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            limit=100,
            startFromHead=False
        )
        
        events = response.get('events', [])
        if not events:
            return f"No tracebacks found mapped to stream: {log_stream_name} within {log_group_name}."
            
        output = [f"--- LAST 100 LOG TRACEBACK EVENTS FOR {log_stream_name} ---"]
        for event in events:
            output.append(event.get('message', ''))
            
        return redact_genomic_phi("\n".join(output), redact_uuids=False)
    except ClientError as e:
        return redact_genomic_phi(f"AWS CloudWatch Logs ClientError: {str(e)}", redact_uuids=False)

@mcp.tool()
def fetch_head_node_log() -> str:
    """
    Linked to workflow: @aws-triage
    Uses an SCP subprocess tunnel to pull the orchestrator's .nextflow.log from the remote EC2 Head Node.
    Returns the last 200 chronological lines of the log payload.
    """
    try:
        subprocess.run([
            "scp", 
            "-i", os.path.expanduser("~/.ssh/ngs-head-node-key.pem"),
            "ec2-user@32.193.91.106:~/ngs-variant-validator/.nextflow.log",
            "/tmp/remote_nextflow.log"
        ], check=True, capture_output=True)
        
        if os.path.exists("/tmp/remote_nextflow.log"):
            with open("/tmp/remote_nextflow.log", "r") as f:
                lines = f.readlines()
            
            tail_lines = lines[-200:] if len(lines) > 200 else lines
            output = ["--- LAST 200 LINES OF HEAD NODE .nextflow.log ---\n"]
            output.extend(tail_lines)
            return redact_genomic_phi("".join(output), redact_uuids=False)
        else:
            return redact_genomic_phi("Failed to locate /tmp/remote_nextflow.log after SCP transfer.", redact_uuids=False)
            
    except subprocess.CalledProcessError as e:
        return redact_genomic_phi(f"SCP Transfer Failed: {e.stderr.decode('utf-8')}", redact_uuids=False)
    except Exception as e:
        return redact_genomic_phi(f"Unexpected Error fetching head node log: {str(e)}", redact_uuids=False)

# --- SSM Telemetry Suite Operations ---

def run_ssm_telemetry_script(script_name: str, job_id: str) -> str:
    """Helper method executing physical bash telemetry strictly in read-only diagnostic bounds."""
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
        result = subprocess.run(
            [sys.executable, script_path, job_id], 
            capture_output=True, 
            text=True, 
            timeout=45
        )
        if result.returncode == 0:
            return redact_genomic_phi(f"SSM Diagnostic Payload [{script_name}]:\n{result.stdout}", redact_uuids=False)
        else:
            return redact_genomic_phi(f"SSM Telemetry Failed ({result.returncode}):\n{result.stderr}\n{result.stdout}", redact_uuids=False)
    except subprocess.TimeoutExpired:
        return redact_genomic_phi(f"FATAL: SSM Tunnel generation hung or exceeded 45-second timeout for {job_id}.", redact_uuids=False)
    except Exception as e:
        return redact_genomic_phi(f"Unexpected SSM invocation error: {str(e)}", redact_uuids=False)

@mcp.tool()
def get_live_container_ram(job_id: str) -> str:
    """
    Linked to skill: @ssm-telemetry-suite
    REQUIRED FOR Zero-Trust Observability: Retrieves the active memory ceiling / OOM metrics
    from a currently 'RUNNING' EC2 AWS Batch container using the live_container_ram.py script natively.
    """
    return run_ssm_telemetry_script("live_container_ram.py", job_id)

@mcp.tool()
def get_live_container_disk(job_id: str) -> str:
    """
    Linked to skill: @ssm-telemetry-suite
    REQUIRED FOR Zero-Trust Observability: Retrieves the physical EBS block capacities (df -h)
    from a stranded 'RUNNING' AWS Batch node dynamically via SSM.
    """
    return run_ssm_telemetry_script("live_container_disk.py", job_id)

@mcp.tool()
def get_live_container_ps(job_id: str) -> str:
    """
    Linked to skill: @ssm-telemetry-suite
    REQUIRED FOR Zero-Trust Observability: Traces Unix sub-process hierarchies mapping (ps auxfw)
    to spot Zombie processes or infinitely hanging Bash scripts inside stranded nodes.
    """
    return run_ssm_telemetry_script("live_container_ps.py", job_id)

if __name__ == "__main__":
    mcp.run()
