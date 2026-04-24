import sqlite3
import pathlib
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

def get_db_path():
    return str(pathlib.Path(__file__).parent / "app.db")

def init_db():
    with sqlite3.connect(get_db_path()) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()

init_db()

@app.get("/", response_class=HTMLResponse)
def read_root():
    with sqlite3.connect(get_db_path()) as conn:
        items = conn.execute("SELECT id, name FROM items").fetchall()
    
    items_html = "".join(f"<li>{item[1]}</li>" for item in items)
    return f"""
    <html>
        <body>
            <form action="/add" method="post">
                <button type="submit">Add Item</button>
            </form>
            <ul>{items_html}</ul>
        </body>
    </html>
    """

@app.post("/add")
def add_item():
    with sqlite3.connect(get_db_path()) as conn:
        conn.execute("INSERT INTO items (name) VALUES ('New Item')")
        conn.commit()
    return RedirectResponse(url="/", status_code=303)
