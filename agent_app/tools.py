import os
import glob
import subprocess
import hmac
import hashlib
from datetime import datetime
import secrets

from .config import BASE_DIR

# --- Native Python Tools for Documentation ---
def list_docs() -> list[str]:
    """Lists all available documentation files tightly bound to zero-trust directories."""
    permitted_dirs = ["docs/director_context", ".agents/rules", ".agents/workflows"]
    all_paths = []
    for d in permitted_dirs:
        all_paths.extend(glob.glob(os.path.join(BASE_DIR, d, "**", "*.md"), recursive=True))
    return sorted([os.path.relpath(p, BASE_DIR) for p in all_paths])

def read_doc(file_path: str) -> str:
    """Reads the full content of a specific documentation file by relative path."""
    if not (file_path.startswith("docs/director_context/") or file_path.startswith(".agents/rules/") or file_path.startswith(".agents/workflows/")):
        return "[SECURITY FATAL] You are not authorized to traverse outside docs/director_context, .agents/rules, or .agents/workflows."
        
    full_path = os.path.join(BASE_DIR, file_path)
    if os.path.exists(full_path) and full_path.endswith('.md'):
        with open(full_path, 'r') as f:
            return f.read()
    return "File not found or not a markdown doc."

def write_retrospective(content: str, title: str) -> str:
    """Writes a markdown retrospective document to the docs/retrospectives directory. Title should be snake_case, no extension."""
    date_str = datetime.now().strftime('%Y-%m-%d')
    mode = os.environ.get("ADK_SWARM_MODE", "")
    if not mode:
        mode = "swarm"
    filename = f"{date_str}_{title}_{mode}.md"
    filepath = os.path.join(BASE_DIR, "docs", "retrospectives", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        f.write(content)
    return f"[SUCCESS] Retrospective written to {filepath}"

def _extract_adk_trace(node, current_author, agent_traces, total_events):
    if isinstance(node, dict):
        author = node.get("author") or node.get("name") or current_author
        
        if "usage_metadata" in node and isinstance(node["usage_metadata"], dict) and author:
            if author not in agent_traces:
                agent_traces[author] = {'count': 0, 'tokens_in': 0, 'tokens_out': 0}
                
            agent_traces[author]['count'] += 1
            total_events[0] += 1
            agent_traces[author]['tokens_in'] += (node["usage_metadata"].get("prompt_token_count") or 0)
            agent_traces[author]['tokens_out'] += (node["usage_metadata"].get("candidates_token_count") or 0)

        for k, v in node.items():
            _extract_adk_trace(v, author if k not in ['usage_metadata', 'actual_invocation'] else author, agent_traces, total_events)
    elif isinstance(node, list):
        for item in node:
            _extract_adk_trace(item, current_author, agent_traces, total_events)

def write_eval_report(test_id: str, content: str, is_passing: bool) -> str:
    """Writes a markdown evaluation report to the docs/evals directory."""
    import time
    import json
    import glob
    import shutil
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    mode = os.getenv("ADK_SWARM_MODE", "swarm")
    
    # 1. Namespace Resolution: Prioritize CI/CD boundary variables, fallback to agent context
    test_name = os.environ.get("ACTIVE_TEST_ID") 
    if not test_name:
        test_name = test_id.strip() if test_id else "unknown_test_id"
        
    test_slug = test_name.replace(' ', '_').lower()
    filename = f"{date_str}_{test_slug}_{mode}_eval.md"
    filepath = os.path.join(BASE_DIR, "docs", "evals", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        status_label = "**Result: [PASS]**" if is_passing else "**Result: [FAIL]**"
        
        # Move any retrospective generated in the last 5 minutes (assumed from this test run)
        retro_dir = os.path.join(BASE_DIR, "docs", "retrospectives")
        dest_dir = os.path.join(BASE_DIR, "docs", "evals", "retrospectives")
        os.makedirs(dest_dir, exist_ok=True)
        
        current_time = time.time()
        for retro_file in glob.glob(os.path.join(retro_dir, f"*_{mode}.md")):
            if os.path.isfile(retro_file):
                if current_time - os.path.getmtime(retro_file) < 300: # 5 minutes
                    dest_file = os.path.join(dest_dir, os.path.basename(retro_file))
                    shutil.move(retro_file, dest_file)
        
        telemetry = "<!-- TELEMETRY_INJECTION_POINT -->\n\n---\n\n"

            
        content = f"{status_label}\n\n" + telemetry + content
    except Exception as e:
        print(f"Failed to inject telemetry: {e}")

    with open(filepath, 'w') as f:
        f.write(content)
    return f"[SUCCESS] Evaluation report written to {filepath}"

# Note: Retrospective routing and directory sorting are now completely decoupled
# and handled natively inside write_eval_report via OS bindings.

# --- Cryptographic State Transition Tools ---
def _get_qa_secret() -> bytes:
    """Fetches the deterministic or dynamic secret for HMAC signing to validate state passes natively."""
    key_file = os.path.join(BASE_DIR, ".agents", "memory", "staging_key.txt")
    if not os.path.exists(key_file):
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, "w") as f:
            f.write(secrets.token_hex(32))
    with open(key_file, "r") as f:
        return f.read().strip().encode('utf-8')

def _qa_signature_path() -> str:
    return os.path.join(BASE_DIR, ".staging", ".qa_signature")

def escalate_to_director(reason: str) -> str:
    """Escalates an unresolvable testing paradox, physical constraint, or tooling limitation back up to the Director."""
    return "[FATAL] State Transition Tool Called: You have safely escalated to the Director."

def mark_qa_passed(summary: str) -> str:
    """Marks the current QA evaluation cycle as PASSED. Use this ONLY when test arrays securely exit with code 0."""
    staging_dir = os.path.join(BASE_DIR, ".staging")
    os.makedirs(staging_dir, exist_ok=True)
    sig = hmac.new(_get_qa_secret(), b"QA_PASSED", hashlib.sha256).hexdigest()
    sig_path = _qa_signature_path()
    with open(sig_path, "w") as f:
        f.write(sig)
    return f"[SUCCESS] State Transition Tool Called: QA Passed. HMAC signature written to .staging/.qa_signature"

def approve_staging_qa(summary: str) -> str:
    """Approves the Architect's evaluation of the QA loop, securely vetting the staging payload for the Auditor."""
    sig_path = _qa_signature_path()
    if not os.path.exists(sig_path):
        return (
            "[BLOCKED] Cannot approve staging: .staging/.qa_signature does not exist. "
            "The QA Engineer must invoke mark_qa_passed after a successful test run. "
            "Route control back to the QA Engineer."
        )
    with open(sig_path, "r") as f:
        stored_sig = f.read().strip()
    expected_sig = hmac.new(_get_qa_secret(), b"QA_PASSED", hashlib.sha256).hexdigest()
    if not hmac.compare_digest(stored_sig, expected_sig):
        return (
            "[BLOCKED] Cannot approve staging: .staging/.qa_signature contains an invalid HMAC. "
            "The cryptographic gate has been tampered with or was written by an unauthorized process."
        )
    return "[SUCCESS] State Transition Tool Called: Staging QA Vetted. HMAC signature verified."

def mark_system_complete() -> str:
    """Flags the global architectural directive as 100% physically complete across all constraints."""
    return "[SUCCESS] State Transition Tool Called: System Complete."

def run_pipeline_diagnostics() -> str:
    """Natively executes the global Pytest suite to generate a systemic traceback array of all failing backend tests. Skips OSX docker keychain tests."""
    venv_pytest = os.path.join(BASE_DIR, "venv", "bin", "pytest")
    if not os.path.exists(venv_pytest):
        return "[ERROR] venv/bin/pytest not found."
    
    cmd = [venv_pytest, os.path.join(BASE_DIR, "tests"), "-k", "not docker", "--tb=short", "-q"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
        output = result.stdout + "\n" + result.stderr
        if len(output) > 8000:
            return output[:8000] + "\n\n... [TRUNCATED] ..."
        return output
    except Exception as e:
        return "[ERROR] Failed to run pipeline: " + str(e)

def research_read_file(file_path: str) -> str:
    """Reads a file natively in the workspace for research purposes."""
    if os.path.isabs(file_path) and file_path.startswith(BASE_DIR):
        file_path = os.path.relpath(file_path, BASE_DIR)
    target_path = os.path.join(BASE_DIR, file_path)
    if os.path.exists(target_path) and os.path.isfile(target_path):
        with open(target_path, 'r') as f:
            return f.read()
    return f"[ERROR] File not found: {file_path}"

def research_list_directory(dir_path: str) -> str:
    """Lists files in a directory for research purposes."""
    if os.path.isabs(dir_path) and dir_path.startswith(BASE_DIR):
        dir_path = os.path.relpath(dir_path, BASE_DIR)
    target_path = os.path.join(BASE_DIR, dir_path)
    if os.path.exists(target_path) and os.path.isdir(target_path):
        return "\n".join(os.listdir(target_path))
    return f"[ERROR] Directory not found: {dir_path}"
