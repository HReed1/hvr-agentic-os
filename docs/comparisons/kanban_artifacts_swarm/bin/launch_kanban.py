import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Dynamic path injection for survival
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.models_kanban import Base, Board, Column, Task
from api.routers.kanban import router, get_db

app = FastAPI()
app.include_router(router)

DB_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./kanban.db")
engine = create_async_engine(DB_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_db_override():
    async with async_session() as session:
        yield session

app.dependency_overrides[get_db] = get_db_override

@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")
    with open(template_path, "r") as f:
        return f.read()

def seed_db():
    # Sync engine for seeding - use the same file as async
    sync_url = DB_URL.replace("+aiosqlite", "")
    sync_engine = create_engine(sync_url)
    Base.metadata.create_all(sync_engine)
    
    Session = sessionmaker(bind=sync_engine)
    with Session() as session:
        if not session.query(Board).first():
            board = Board(name="Board 1")
            session.add(board)
            session.commit()
            
            cols = [
                Column(name="To Do", board_id=board.id, order=1),
                Column(name="Doing", board_id=board.id, order=2),
                Column(name="Done", board_id=board.id, order=3)
            ]
            session.add_all(cols)
            session.commit()

if __name__ == "__main__":
    if os.environ.get("SEED_ONLY"):
        seed_db()
        sys.exit(0)
        
    seed_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
