import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

from api.models_kanban import Base, Board, KanbanColumn
from api.routers.kanban import router as kanban_router, engine, AsyncSessionLocal
from sqlalchemy.future import select

app = FastAPI(title="Kanban Board")

app.include_router(kanban_router)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    template_path = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Board).where(Board.name == "Board 1"))
        board = result.scalars().first()
        if not board:
            board = Board(name="Board 1")
            session.add(board)
            await session.commit()
            await session.refresh(board)
            
            for col_name in ["To Do", "Doing", "Done"]:
                col = KanbanColumn(name=col_name, board_id=board.id)
                session.add(col)
            await session.commit()

@app.on_event("startup")
async def startup_event():
    await init_db()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
