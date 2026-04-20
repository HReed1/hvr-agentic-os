import os
import subprocess
import sys
from mcp.server.fastmcp import FastMCP

# Ensure local imports resolve when called natively by the MCP Host process
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.nextflow_ast import extract_dsl2_block
from utils.dlp_proxy import redact_genomic_phi
from utils.staging_lease import acquire_staging_lease
import shutil
import hmac
import hashlib

def get_secret() -> bytes:
    # Deterministic simulation secret for cryptographic signing
    return b"NGS_ZERO_TRUST_SIMULATION_KEY_2026"

mcp = FastMCP("TDAID AST Validation Server")

@mcp.tool()
def parse_nextflow_ast(script_path: str, target_process: str) -> str:
    """
    Linked to skill: @tdaid-ast-assertion
    Extracts a fully enclosed DSL2 process or workflow block from a Nextflow script 
    without regex truncations. Essential for structurally updating the DSL2 context.
    """
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        block = extract_dsl2_block(content, target_process)
        if not block:
            return redact_genomic_phi(f"Error: Target '{target_process}' not found or improperly formatted in {script_path}.", redact_uuids=False)
        return redact_genomic_phi(block, redact_uuids=False)
    except FileNotFoundError:
        return redact_genomic_phi(f"Error: The script {script_path} does not exist.", redact_uuids=False)
    except Exception as e:
        return redact_genomic_phi(f"Error reading AST: {str(e)}", redact_uuids=False)

@mcp.tool()
def read_staged_file(file_path: str) -> str:
    """
    Linked to workflow: @tdaid-audit.
    Allows the QA Engineer to securely read the proposed `.staging/` validation scripts 
    prior to execution to explicitly rule out Zero-Trust/Host OS mutation violations.
    """
    staging_dir = os.path.abspath(os.path.join(current_dir, "..", ".staging"))
    
    if not file_path.startswith(".staging/"):
        file_path = f".staging/{file_path}"
        
    target_path = os.path.abspath(os.path.join(current_dir, "..", file_path))
    
    if not target_path.startswith(staging_dir):
        return redact_genomic_phi("[SECURITY FATAL] Directory traversal attempt detected outside .staging environment.", redact_uuids=False)
        
    try:
        with acquire_staging_lease(exclusive=False):
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()
                if len(content) > 50000:
                    return f"[SECURITY FATAL] Staged file {file_path} exceeds 50000 bytes. Reject this patch as a hallucination immediately."
                
                # Vertex AI Semantic Offload Protocol
                rag_config_path = os.path.join(project_root, ".agents", "memory", "vertex_rag_config.txt")
                if os.path.exists(rag_config_path) and len(content) > 500:
                    try:
                        with open(rag_config_path, "r") as rcf:
                            corpus_id = rcf.read().strip()
                        import vertexai
                        from vertexai.preview import rag
                        vertexai.init(project="general-477613", location="us-west1")
                        
                        # Ingest the physical script into the GCP vector database
                        response = rag.upload_file(corpus_name=corpus_id, path=target_path, display_name=os.path.basename(target_path))
                        return f"[RAG INGESTION SUCCESS] The file {file_path} ({len(content)} bytes) was uploaded to Corpus {corpus_id}. Please use your VertexAiRagTool to query its contents and extract exact functions."
                    except Exception as e:
                        print(f"RAG Upload failed, falling back to raw string. Err: {e}")

                return redact_genomic_phi(content, redact_uuids=False)
    except BlockingIOError as e:
        return str(e)
    except FileNotFoundError:
        return redact_genomic_phi(f"Error: Proposed staging file {file_path} not found.", redact_uuids=False)
    except Exception as e:
        return redact_genomic_phi(f"Unexpected error: {str(e)}", redact_uuids=False)

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
            env["DB_USER"] = os.environ.get("DB_USER", "postgres")
            env["DB_PASSWORD"] = os.environ.get("DB_PASSWORD", "postgres")
            env["AUTH0_DOMAIN"] = os.environ.get("AUTH0_DOMAIN", "test.auth0.com")
            env["AUTH0_API_AUDIENCE"] = os.environ.get("AUTH0_API_AUDIENCE", "test-audience")

            # Zero-Trust Physical Copy Bridge: To prevent Python module-shadowing paradoxes
            # and avoid Symlink Penetration Traps during executor mutations, we mirror files physically.
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

            # Zero-Trust Dependency Sync: If the Executor mutated dependencies, install them into the venv first
            staged_reqs_path = os.path.join(staging_dir, "requirements.txt")
            if os.path.exists(staged_reqs_path):
                # We quietly install so the Pytest output remains the sole string returned to the Swarm
                subprocess.run([venv_pip, "install", "-r", staged_reqs_path], capture_output=True, env=env)

            result = subprocess.run(
                [venv_pytest, test_path, "-v", "--tb=short"], 
                capture_output=True, 
                text=True, 
                timeout=300,
                cwd=staging_dir,
                env=env
            )
            
            output_limit = 2500 # Ensure we don't breach MCP string size caps implicitly
            
            if result.returncode == 0:
                # Decoupled Payload: Physically write cryptographic signature to disk so Executor can't forge it in prompt.
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
def fuzz_telemetry_webhook(run_id: str = "TDAID-TEST-001", status: str = "COMPLETED", use_valid_secret: bool = True) -> str:
    """
    Linked to workflow: @tdaid-audit & skill: @tdaid-ast-assertion
    Synthesizes a Nextflow weblog DAG payload and POSTs it directly to the local FastAPI telemetry hook.
    Allows the Swarm to assert API zero-trust bounds and database ingestion without booting AWS clusters.
    """
    import urllib.request
    import json
    import os
    
    url = "http://localhost:8000/samples/telemetry/hook"
    secret = "dev-secret-string" if use_valid_secret else "invalid-hacker-string"
    
    # Construct a synthetic Nextflow Weblog payload
    payload = {
        "runName": run_id,
        "runId": "12345-abcde",
        "event": "process_completed",
        "utcTime": "2026-04-14T12:00:00Z",
        "trace": {
            "task_id": 1,
            "status": status,
            "hash": "123456",
            "name": f"{status}-SIMULATION",
            "exit": 0,
            "realtime": 5000,
            "module": ["test_module"]
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    # Use query params string mimicking Nextflow
    req.full_url = f"{url}?m2m_token={secret}"
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            return f"[SUCCESS] Webhook Fuzzer executed (Status Code: {response.status}). Response: {res_body}"
    except urllib.error.HTTPError as e:
        return f"[HTTP ERROR] Fuzzer hit an API boundary. Code: {e.code}. Reason: {e.reason}"
    except Exception as e:
        return f"[FATAL] Fuzzer unable to reach localhost:8000. Is FastAPI running? Err: {str(e)}"

if __name__ == "__main__":
    mcp.run()
