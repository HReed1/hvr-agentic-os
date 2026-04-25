#!/usr/bin/env python3
"""
ADK Trace Importer (JSON to SQLite Bridge)

Natively parses the raw headless execution graphs from `.adk/eval_history/`
and writes the mapped temporal paths directly into `.adk/session.db`. 
By dynamically mutating the `user_id` context to `"user"` and clipping the 
evaluation prefixes, it unblocks interactive trace rendering in the ADK Dev UI.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def unlock_json_traces(agent_dir: Path):
    db_path = agent_dir / ".adk" / "session.db"
    eval_history = agent_dir / ".adk" / "eval_history"
    
    print(f"Connecting to ADK UI Metrics Engine: {db_path}")
    if not db_path.exists():
        print(f"[FATAL] Database {db_path} not found. Boot agent_app first.")
        return
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    json_files = list(eval_history.glob("*.evalset_result.json"))
    if not json_files:
        print("[INFO] No json evaluations localized in the cache.")
        return
        
    imported_count = 0
    skipped = 0
    
    for eval_file in json_files:
        with open(eval_file, 'r') as f:
            data = json.load(f)
            
        for case in data.get('eval_case_results', []):
            session_details = case.get('session_details', {})
            if not session_details:
                continue
                
            orig_id = session_details.get('id')
            if not orig_id:
                continue
                
            # Rewrite metadata contexts 
            app_name = session_details.get('app_name', 'agent_app')
            state_json = json.dumps(session_details.get('state', {}))
            update_time = session_details.get('last_update_time', datetime.now().timestamp())
            
            # Form UI Context Namespace
            new_id = orig_id.replace('___eval___session___', 'evaltrace_')
            new_user_id = 'user'
            
            cur.execute("SELECT 1 FROM sessions WHERE id = ? AND user_id = ?", (new_id, new_user_id))
            if cur.fetchone():
                skipped += 1
                continue
                
            try:
                # 1. Synthesize explicit UI Node
                cur.execute("""
                    INSERT INTO sessions (app_name, user_id, id, state, create_time, update_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (app_name, new_user_id, new_id, state_json, update_time, update_time))
                
                # 2. Bridge Sub-Execution Nodes
                events = session_details.get('events', [])
                for ev in events:
                    ev_id = ev.get('id')
                    inv_id = ev.get('invocation_id')
                    ts = ev.get('timestamp')
                    ev_data = json.dumps(ev)
                    
                    cur.execute("""
                        INSERT INTO events (id, app_name, user_id, session_id, invocation_id, timestamp, event_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (ev_id, app_name, new_user_id, new_id, inv_id, ts, ev_data))
                    
                imported_count += 1
                print(f"[SUCCESS] Uploaded trace matrix -> {new_id} ({len(events)} temporal events)")
                
            except sqlite3.IntegrityError as e:
                print(f"[WARN] Failed mapping matrix {new_id}: {e}")
                
    conn.commit()
    conn.close()
    
    print(f"\n[COMPLETE] Extracted {imported_count} traces natively into SQlite ({skipped} preserved/skipped)!")
    print("Refresh your browser dashboard natively into Session Select!")

if __name__ == '__main__':
    agent_dir = Path(__file__).parent.parent / "agent_app"
    unlock_json_traces(agent_dir)
