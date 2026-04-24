from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import time
import sqlite3
import pathlib

app = FastAPI()

DB_PATH = pathlib.Path(__file__).parent.parent / "app.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)")
    conn.commit()
    conn.close()

init_db()

@app.get("/api/v1/ping")
async def ping():
    return {"status": "pong", "timestamp": time.time()}


@app.get('/live')
async def liveness_probe():
    return {"status": "live"}


@app.get("/items", response_class=HTMLResponse)
async def get_items():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM items")
    items = c.fetchall()
    conn.close()
    
    items_html = "".join([f"<li>{item[0]}</li>" for item in items])
    
    html_content = f"""
    <html>
        <head><title>Items</title></head>
        <body>
            <h1>Items List</h1>
            <ul>
                {items_html}
            </ul>
            <form action="/items" method="post">
                <input type="text" name="item_name" required>
                <button type="submit">Add Item</button>
            </form>
        </body>
    </html>
    """
    return html_content

@app.post("/items")
async def add_item(item_name: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO items (name) VALUES (?)", (item_name,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/items", status_code=303)
