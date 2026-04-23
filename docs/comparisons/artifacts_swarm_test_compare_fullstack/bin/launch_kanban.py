import sys
import os
import asyncio
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy import select

# Anchor explicit path logic for robust exfiltration
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.models_kanban import init_db, async_session, Board, Column
from api.routers.kanban import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with async_session() as session:
        res = await session.execute(select(Board).where(Board.id == 1))
        board = res.scalar_one_or_none()
        if not board:
            board = Board(name="Board 1")
            session.add(board)
            await session.flush()
            cols = [
                Column(name="To Do", board_id=board.id),
                Column(name="Doing", board_id=board.id),
                Column(name="Done", board_id=board.id)
            ]
            session.add_all(cols)
            await session.commit()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/")
async def get_index():
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html"))
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run("bin.launch_kanban:app", host="127.0.0.1", port=8000, reload=False)
