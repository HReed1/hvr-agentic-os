import os
import glob
import json
import sqlite3
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

def main():
    test_name = os.environ.get("ACTIVE_TEST_ID")
    if not test_name:
        print("[Telemetry Injection] ACTIVE_TEST_ID not set. Aborting.")
        return

    # Extract deterministic session trace ID
    session_id_str = ""
    try:
        db_path = os.path.join(BASE_DIR, "agent_app", ".adk", "session.db")
        if os.path.exists(db_path):
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM sessions WHERE id LIKE 'evaltrace_%' ORDER BY create_time DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    session_id_str = row[0]
    except Exception as e:
        print(f"[Telemetry Injection] Failed to query sqlite db: {e}")

    # Extract historical execution trace for exactly this test ID
    eval_dir = os.path.join(BASE_DIR, "agent_app", ".adk", "eval_history")
    if not os.path.exists(eval_dir):
        print("[Telemetry Injection] No ADK eval_history directory found. Aborting.")
        return
        
    all_trace_files = glob.glob(os.path.join(eval_dir, "*.json"))
    all_trace_files.sort(key=os.path.getmtime, reverse=True)
    
    target_file = None
    for tf in all_trace_files:
        try:
            with open(tf, "r", encoding="utf-8") as f:
                trace_data = json.load(f)
                if trace_data.get("eval_set_id") == test_name:
                    target_file = tf
                    break
        except Exception:
            continue
            
    if not target_file:
        print(f"[Telemetry Injection] No trace JSON mapped to {test_name}. Aborting.")
        return

    # Process metrics
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        total_events = [0]
        agent_traces = {}
        _extract_adk_trace(data, None, agent_traces, total_events)
        
        telemetry = ""
        if session_id_str:
            telemetry += f"**ADK Session ID:** `{session_id_str}`\n"
        telemetry += f"**Execution Source:** `{os.path.basename(target_file)}`\n"
        telemetry += f"**Total LLM Inferences:** `{total_events[0]}`\n\n"
        telemetry += "### Trace Breakdown\n"
        
        if not agent_traces:
             telemetry += "- (No LLM execution bounds recorded in target trace)\n"
             
        for author, stats in sorted(agent_traces.items()):
            token_str = f" [In: {stats['tokens_in']:,} | Out: {stats['tokens_out']:,}]"
            telemetry += f"- **{author}**: {stats['count']} inferences{token_str}\n"

    except Exception as e:
        print(f"[Telemetry Injection] Error unpacking target trace file: {e}")
        return

    # Find the matching markdown file
    test_slug = test_name.replace(' ', '_').lower()
    search_pattern = os.path.join(BASE_DIR, "docs", "evals", f"*_{test_slug}_swarm_eval.md")
    md_files = glob.glob(search_pattern)
    if not md_files:
        print(f"[Telemetry Injection] Markdown file matching {test_slug} not found.")
        return
        
    md_files.sort(key=os.path.getmtime, reverse=True)
    target_md = md_files[0]
    
    with open(target_md, "r", encoding="utf-8") as f:
        md_content = f.read()

    new_content = md_content.replace("<!-- TELEMETRY_INJECTION_POINT -->", telemetry)

    with open(target_md, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"[Telemetry Injection] Successfully merged trace {os.path.basename(target_file)} into {os.path.basename(target_md)}")

if __name__ == "__main__":
    main()
