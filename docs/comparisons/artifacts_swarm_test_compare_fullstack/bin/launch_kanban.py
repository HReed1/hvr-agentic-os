import sys
import os
import uvicorn
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from api.routers.kanban import router

app = FastAPI()
app.include_router(router)

def seed_db():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kanban.db"))
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS columns (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            board_id INTEGER,
            FOREIGN KEY(board_id) REFERENCES boards(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title VARCHAR NOT NULL,
            description VARCHAR NOT NULL,
            tags VARCHAR NOT NULL,
            column_id INTEGER,
            FOREIGN KEY(column_id) REFERENCES columns(id)
        )
    """)
    cur.execute("SELECT COUNT(*) FROM boards")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO boards (name) VALUES ('Board 1')")
        board_id = cur.lastrowid
        cur.execute("INSERT INTO columns (name, board_id) VALUES ('To Do', ?)", (board_id,))
        cur.execute("INSERT INTO columns (name, board_id) VALUES ('Doing', ?)", (board_id,))
        cur.execute("INSERT INTO columns (name, board_id) VALUES ('Done', ?)", (board_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
