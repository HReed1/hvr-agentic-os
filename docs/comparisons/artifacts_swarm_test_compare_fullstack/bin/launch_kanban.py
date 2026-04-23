import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from api.routers.kanban import router as kanban_router, engine, Base
from api.models_kanban import Board, Column
from sqlalchemy import select

app = FastAPI(title="Kanban Board Native")
app.include_router(kanban_router)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    from api.routers.kanban import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Board).where(Board.id == 1))
        board = result.scalar_one_or_none()
        if not board:
            board = Board(name="Board 1")
            session.add(board)
            await session.commit()
            await session.refresh(board)
            
            cols = ["To Do", "Doing", "Done"]
            for c in cols:
                session.add(Column(name=c, board_id=board.id))
            await session.commit()

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    template_path = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")
    with open(template_path, "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("KANBAN_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)