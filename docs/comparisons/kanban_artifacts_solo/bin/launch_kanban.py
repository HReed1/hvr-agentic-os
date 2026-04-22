import sys
import os
import contextlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.future import select

from api.models_kanban import Base, Board, Column
from api.routers.kanban import router as kanban_router, get_db

DB_URL = "sqlite+aiosqlite:///./kanban.db"
engine = create_async_engine(DB_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Board).where(Board.name == "Board 1"))
        board = res.scalar_one_or_none()
        if not board:
            board = Board(name="Board 1")
            session.add(board)
            await session.commit()
            await session.refresh(board)
            
            c1 = Column(name="To Do", board_id=board.id)
            c2 = Column(name="Doing", board_id=board.id)
            c3 = Column(name="Done", board_id=board.id)
            session.add_all([c1, c2, c3])
            await session.commit()
            
    yield

app = FastAPI(lifespan=lifespan)
app.dependency_overrides[get_db] = get_db_session
app.include_router(kanban_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run("launch_kanban:app", host="127.0.0.1", port=8000, reload=False)
