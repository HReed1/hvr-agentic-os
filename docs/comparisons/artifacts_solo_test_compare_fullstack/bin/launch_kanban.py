import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

from api.models_kanban import Base, Board, Column
from api.routers.kanban import router, engine, AsyncSessionLocal

app = FastAPI()

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Board).where(Board.id == 1))
        board = result.scalar_one_or_none()
        if not board:
            board = Board(id=1, name="Board 1")
            session.add(board)
            await session.commit()
            
            for col_name in ["To Do", "Doing", "Done"]:
                session.add(Column(name=col_name, board_id=board.id))
            await session.commit()

@app.get("/", response_class=HTMLResponse)
async def serve_kanban():
    template_path = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
