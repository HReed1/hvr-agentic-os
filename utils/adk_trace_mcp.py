import sys
import os
import json
import sqlite3
from typing import Optional
from mcp.server.fastmcp import FastMCP

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Allow the DB path to be overridden via env var so worktree sessions are
# readable without modifying this script. Set ADK_SESSION_DB in .mcp.json env.
_DEFAULT_DB_PATH = os.path.join(project_root, "agent_app", ".adk", "session.db")
ADK_SESSION_DB = os.environ.get("ADK_SESSION_DB", _DEFAULT_DB_PATH)

mcp = FastMCP("ADK Trace Reader")

@mcp.tool()
def get_latest_adk_session(max_events: int = 50, session_id: Optional[str] = None) -> str:
    """
    Retrieves and summarizes the execution trace from the ADK SQLite session database.
    If session_id is not provided, it fetches the most recent session automatically.
    Returns a formatted markdown timeline of the swarm's execution, capturing tool calls, 
    agent instructions, errors, and text responses.
    """
    db_path = ADK_SESSION_DB
    if not os.path.exists(db_path):
        # Fallback to look at downloads dir
        downloads_dir = os.path.expanduser("~/Downloads")
        import glob
        json_files = glob.glob(os.path.join(downloads_dir, "session-*.json"))
        if not json_files:
            return f"Error: Cannot find local DB {db_path} or any exports in ~/Downloads."
        latest_file = max(json_files, key=os.path.getctime)
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
                events = data.get('events', []) if isinstance(data, dict) else data
                return _format_events(events[-max_events:])
        except Exception as e:
            return f"Error reading JSON export: {str(e)}"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if not session_id:
            # If the tool is invoked by the meta-evaluator, we MUST skip its own active session
            # and target the headless Swarm trace explicitly using the evaltrace prefix constraint.
            if os.environ.get("ADK_SWARM_MODE") == "meta_eval":
                cursor.execute("SELECT id FROM sessions WHERE id LIKE 'evaltrace_%' ORDER BY create_time DESC LIMIT 1;")
            else:
                cursor.execute("SELECT id FROM sessions ORDER BY create_time DESC LIMIT 1;")
            
            row = cursor.fetchone()
            if not row:
                return "No sessions found in database."
            session_id = row['id']
            
        # Optional safeguard for trace reader: double check if the session is empty
        cursor.execute("SELECT event_data FROM events WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
        rows = cursor.fetchall()

        events = []
        for r in rows:
            events.append(json.loads(r['event_data']))
            
        recent_events = events[-max_events:] if len(events) > max_events else events
        
        output = [f"### Session Trace ({session_id})"]
        output.append(f"Total events in session: {len(events)}. Showing last {len(recent_events)}.\n")
        
        output.append(_format_events(recent_events))
        return "\n".join(output)

    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        if 'conn' in locals():
            conn.close()

def _format_events(events) -> str:
    lines = []
    for idx, event in enumerate(events, 1):
        if not isinstance(event, dict):
            lines.append(f"**(Node #{idx}) [System]**: [Raw Data]\n{str(event)[:200]}\n")
            continue
            
        author = event.get('author') or 'System'
        content = event.get('content') or {}
        actions = event.get('actions') or {}
        
        if not isinstance(content, dict):
            content = {}
            
        role = content.get('role', 'unknown')
        parts = content.get('parts', [])
        if not isinstance(parts, list):
            parts = []
            
        action_str = ""
        if isinstance(actions, dict) and actions:
            action_parts = []
            for k, v in actions.items():
                if v: # Highlight truthy graph transformations like escalate=True
                    action_parts.append(f"{k}={v}")
            if action_parts:
                action_str = f" [ACTIONS: {', '.join(action_parts)}]"

        header = f"**(Node #{idx}) [{author}] ({role}){action_str}**"
        
        for part in parts:
            if not isinstance(part, dict):
                continue
                
            if 'text' in part and isinstance(part['text'], str):
                text = part['text'].strip()
                if len(text) > 2000:
                    text = text[:2000] + "\n...[TRUNCATED_FOR_LENGTH]"
                lines.append(f"{header}:\n{text}\n")
            elif 'function_call' in part or 'functionCall' in part:
                fc = part.get('function_call') or part.get('functionCall') or {}
                name = fc.get('name', 'unknown_tool')
                args = json.dumps(fc.get('args', {}), indent=2)
                lines.append(f"{header} called tool `{name}`:\n```json\n{args}\n```\n")
            elif 'function_response' in part or 'functionResponse' in part:
                fr = part.get('function_response') or part.get('functionResponse') or {}
                name = fr.get('name', 'unknown_tool')
                resp_str = json.dumps(fr.get('response', {}), indent=2)
                if len(resp_str) > 2000:
                    resp_str = resp_str[:2000] + "\n...[TRUNCATED_FOR_LENGTH]"
                lines.append(f"{header} response from `{name}`:\n```json\n{resp_str}\n```\n")
            else:
                lines.append(f"{header}: [Unknown Content Type]\n{json.dumps(part)[:200]}\n")
                
    return "\n".join(lines)

import subprocess

@mcp.tool()
def generate_session_animation(session_id: Optional[str] = None) -> str:
    """
    Creates an interactive HTML animation of the swarm's execution for a given ADK session.
    If session_id is not provided, it fetches the most recent session automatically.
    Returns the path to the generated HTML file and success status.
    """
    db_path = ADK_SESSION_DB
    
    try:
        # Determine session ID if none provided
        if not session_id:
            if not os.path.exists(db_path):
                return "Error: Database not found. Please provide an explicit session_id."
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM sessions ORDER BY create_time DESC LIMIT 1;")
            row = cursor.fetchone()
            conn.close()
            if not row:
                return "No sessions found in database."
            session_id = row['id']
            
        script_path = os.path.join(project_root, "generate_animation.py")
        if not os.path.exists(script_path):
            return f"Error: Animation script not found at {script_path}"
            
        # Execute the standalone CLI generation script natively
        result = subprocess.run(
            [sys.executable, script_path, session_id],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            return f"Successfully generated animation for session {session_id}.\n\nSTDOUT:\n{result.stdout}"
        else:
            return f"Failed to generate animation. Error:\nSTDERR: {result.stderr}\nSTDOUT: {result.stdout}"
            
    except Exception as e:
        return f"Error executing animation generator: {str(e)}"

@mcp.tool()
def generate_global_scorecard() -> str:
    """
    Run the global evaluation scorecard script and return its parsed markdown content.
    Returns the final pass rate and the summary of the tests run.
    """
    script_path = os.path.join(project_root, "utils", "generate_global_eval_report.py")
    if not os.path.exists(script_path):
        return f"Error: Global eval report script not found at {script_path}"
        
    try:
        # Execute the standalone CLI evaluation generation script natively
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        scorecard_path = os.path.join(project_root, "docs", "evals", "GLOBAL_EVAL_SCORECARD.md")
        if os.path.exists(scorecard_path):
            with open(scorecard_path, "r", encoding="utf-8") as f:
                content = f.read()
            return f"Successfully generated global scorecard.\n\nSTDOUT:\n{result.stdout}\n\nCONTENT:\n{content}"
        
        return f"Successfully ran script, but scorecard artifact was missing.\nSTDOUT:\n{result.stdout}"
    except Exception as e:
        return f"Error executing global eval report generator: {str(e)}"

@mcp.tool()
def import_eval_traces() -> str:
    """
    Parses evaluating JSON matrices natively from .adk/eval_history and imports 
    them structurally into the standard SQLite ADK Database without EVAL masks.
    This seamlessly bridges headless telemetry arrays directly into the React GUI.
    """
    script_path = os.path.join(project_root, "bin", "adk-trace-importer.py")
    if not os.path.exists(script_path):
        return f"Error: Trace importer script not found at {script_path}"
        
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            return f"Successfully unlocked headless JSON traces into the session UI.\n\nSTDOUT:\n{result.stdout}"
        else:
            return f"Failed to unlock evaluation traces. Error:\nSTDERR: {result.stderr}\nSTDOUT: {result.stdout}"
            
    except Exception as e:
        return f"Error executing trace importer: {str(e)}"

if __name__ == "__main__":
    mcp.run()
