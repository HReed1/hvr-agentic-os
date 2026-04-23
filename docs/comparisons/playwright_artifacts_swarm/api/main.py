from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, select
import time

DATABASE_URL = "sqlite+aiosqlite:///app.db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

app = FastAPI()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/api/v1/ping")
async def ping():
    return {"status": "pong", "timestamp": time.time()}

@app.get("/live")
async def liveness_probe():
    return {"status": "live"}

@app.get("/", response_class=HTMLResponse)
async def read_root(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    items = result.scalars().all()
    
    items_html = "".join([f"<li>{item.name}</li>" for item in items])
    
    html_content = f"""
    <html>
        <head>
            <title>CRUD Interface</title>
        </head>
        <body>
            <h1>Items</h1>
            <ul id="item-list">
                {items_html}
            </ul>
            <form action="/items" method="post">
                <input type="text" name="name" id="item-name" required />
                <button type="submit" id="add-item-btn">Add Item</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/items", response_class=RedirectResponse)
async def create_item(name: str = Form(...), db: AsyncSession = Depends(get_db)):
    new_item = Item(name=name)
    db.add(new_item)
    await db.commit()
    return RedirectResponse(url="/", status_code=303)
