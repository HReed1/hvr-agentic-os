import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Inject root directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.routers.kanban import router as kanban_router
from api.database import engine, AsyncSessionLocal
from api.models_kanban import Base, Board, BoardColumn

app = FastAPI()
app.include_router(kanban_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def get_home():
    template_path = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")
    with open(template_path, "r") as f:
        return f.read()

async def seed_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy.future import select
        result = await session.execute(select(Board).filter(Board.name == "Board 1"))
        board = result.scalars().first()
        if not board:
            board = Board(name="Board 1")
            session.add(board)
            await session.commit()
            await session.refresh(board)
            
            for col_name in ["To Do", "Doing", "Done"]:
                col = BoardColumn(name=col_name, board_id=board.id)
                session.add(col)
            await session.commit()

@app.on_event("startup")
async def startup_event():
    await seed_db()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)