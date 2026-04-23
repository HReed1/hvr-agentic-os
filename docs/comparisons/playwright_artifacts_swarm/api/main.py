from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import time
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import select

DATABASE_URL = "sqlite+aiosqlite:///app.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/", response_class=HTMLResponse)
async def get_items():
    async with async_session() as session:
        result = await session.execute(select(Item))
        items = result.scalars().all()
    
    items_html = "".join([f'<div class="item">{item.name}</div>' for item in items])
    html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>CRUD Interface</title>
        </head>
        <body>
            <h1>Items</h1>
            <div id="items-list">{items_html}</div>
            <form action="/add" method="post">
                <input type="text" name="name" value="New Item" />
                <button type="submit">Add Item</button>
            </form>
        </body>
    </html>
    """
    return html

@app.post("/add", response_class=RedirectResponse)
async def add_item(name: str = Form(...)):
    async with async_session() as session:
        new_item = Item(name=name)
        session.add(new_item)
        await session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/api/v1/ping")
async def ping():
    return {"status": "pong", "timestamp": time.time()}

@app.get('/live')
async def liveness_probe():
    return {"status": "live"}
