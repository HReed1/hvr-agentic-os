import sys
import os
import asyncio
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
from api.routers.kanban import router as kanban_router, engine, AsyncSessionLocal
from api.models_kanban import Board, Column, Base
from api.models_kanban import Board, Column

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy.future import select
        result = await session.execute(select(Board).where(Board.name == "Board 1"))
        board = result.scalars().first()
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(kanban_router, prefix="/api")

@app.get("/")
async def serve_kanban():
    template_path = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")
    return FileResponse(template_path)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)