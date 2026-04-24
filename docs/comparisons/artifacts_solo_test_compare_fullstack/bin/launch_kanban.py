import sys
import os
import asyncio
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from api.database import engine, AsyncSessionLocal
from api.models_kanban import Base, Board, BoardColumn
from api.routers import kanban
import uvicorn

app = FastAPI()

app.include_router(kanban.router)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")

@app.get("/", response_class=HTMLResponse)
async def serve_kanban():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()

async def seed_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy.future import select
        res = await session.execute(select(Board).where(Board.id == 1))
        board = res.scalars().first()
        if not board:
            board = Board(name="Board 1")
            session.add(board)
            await session.commit()
            await session.refresh(board)
            
            cols = ["To Do", "Doing", "Done"]
            for c in cols:
                session.add(BoardColumn(name=c, board_id=board.id))
            await session.commit()

@app.on_event("startup")
async def startup_event():
    await seed_database()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)