import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.routers.kanban import router as kanban_router
from api.db_deps import init_db, SessionLocal
from api.models_kanban import Board, Column
from sqlalchemy import select

app = FastAPI(title="Kanban Fullstack")
app.include_router(kanban_router)

@app.get("/")
async def serve_kanban():
    template_path = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

async def seed_db():
    await init_db()
    async with SessionLocal() as session:
        result = await session.execute(select(Board).where(Board.name == "Board 1"))
        board = result.scalars().first()
        if not board:
            board = Board(name="Board 1")
            session.add(board)
            await session.flush()
            session.add_all([
                Column(name="To Do", board_id=board.id),
                Column(name="Doing", board_id=board.id),
                Column(name="Done", board_id=board.id),
            ])
            await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_db())
    uvicorn.run(app, host="0.0.0.0", port=8000)
