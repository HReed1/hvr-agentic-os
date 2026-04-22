import sqlite3, json

conn = sqlite3.connect('agent_app/.adk/session.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('SELECT event_data FROM events WHERE session_id=? ORDER BY timestamp ASC', ('evaltrace_566c57a5-f6c2-4b10-8927-6a68cfa5dba6',))
rows = cursor.fetchall()
conn.close()

for i, row in enumerate(rows):
    ev = json.loads(row['event_data'])
    author = ev.get('author', 'Unknown')
    content = ev.get('content')
    if content and isinstance(content, dict):
        role = content.get('role', 'unknown')
        parts = content.get('parts', [])
        for p in parts:
            if isinstance(p, dict):
                fc = p.get('functionCall') or p.get('function_call')
                if fc:
                    print(f"Node {i} [{author}] Called Tool: {fc.get('name')}")
                elif p.get('text'):
                    txt = p['text'].strip()
                    if 'error' in txt.lower() or 'failed' in txt.lower():
                        print(f"Node {i} [{author}] Text (Error context): {txt[:100].replace(chr(10), ' ')}")
