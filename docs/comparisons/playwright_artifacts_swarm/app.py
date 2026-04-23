from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import sqlite3

def init_db():
    conn = sqlite3.connect("app.db")
    conn.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def get_root():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM items")
    items = cursor.fetchall()
    conn.close()
    
    items_html = "".join(f"<li>{item[0]}</li>" for item in items)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>App</title></head>
    <body>
        <ul>{items_html}</ul>
        <form method="post" action="/add">
            <input type="text" name="name" value="test_item" required/>
            <button type="submit">Add Item</button>
        </form>
    </body>
    </html>
    """

@app.post("/add", response_class=HTMLResponse)
async def add_item(name: str = Form(...)):
    conn = sqlite3.connect("app.db")
    conn.execute("INSERT INTO items (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    
    return "<p>Item added.</p><a href='/'>Go back</a>"
