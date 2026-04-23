import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect('app.db')
    return conn

@app.on_event("startup")
def startup():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
    conn.commit()
    conn.close()

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
        <body>
            <form action="/add" method="post">
                <button type="submit">Add Item</button>
            </form>
        </body>
    </html>
    """

@app.post("/add", response_class=HTMLResponse)
async def add_item():
    conn = get_db_connection()
    conn.execute("INSERT INTO items (name) VALUES ('Test')")
    conn.commit()
    conn.close()
    return """
    <html>
        <body>
            <p>Item added</p>
        </body>
    </html>
    """
