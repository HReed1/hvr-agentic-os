import os
import sys
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

# Anchoring
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.models_kanban import Base, Board, Column
from api.routers.kanban import router as kanban_router

DB_URL = "sqlite+aiosqlite:///kanban.db"
engine = create_async_engine(DB_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

app = FastAPI()

async def get_db():
    async with async_session() as session:
        yield session

# Dependency injection for the router
@app.middleware("http")
async def db_session_middleware(request, call_next):
    async with async_session() as session:
        request.state.db = session
        response = await call_next(request)
        return response

async def get_db_override():
    async with async_session() as session:
        yield session

app.include_router(kanban_router)
app.dependency_overrides[kanban_router.dependencies[0].dependency if kanban_router.dependencies else None] = get_db_override
# Better: import get_db directly
from api.routers.kanban import get_db
app.dependency_overrides[get_db] = get_db_override
# Since I already wrote the router with `db: AsyncSession`, I will use a dependency override.

@app.get("/", response_class=HTMLResponse)
async def get_index():
    template_path = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")
    with open(template_path, "r") as f:
        return f.read()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        # Seeding
        stmt = select(Board).where(Board.name == "Board 1")
        result = await session.execute(stmt)
        if not result.scalar_one_or_none():
            board = Board(name="Board 1")
            session.add(board)
            await session.commit()
            await session.refresh(board)
            
            for col_name in ["To Do", "Doing", "Done"]:
                col = Column(name=col_name, board_id=board.id)
                session.add(col)
            await session.commit()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
