import os
import sys
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Anchoring
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.routers.kanban import router as kanban_router
from api.database import engine, async_session
from api.models_kanban import Base, Board, ColumnModel

app = FastAPI()

app.include_router(kanban_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seeding
    async with async_session() as session:
        from sqlalchemy.future import select
        result = await session.execute(select(Board).where(Board.id == 1))
        board = result.scalars().first()
        if not board:
            new_board = Board(name="Board 1")
            session.add(new_board)
            await session.flush()
            
            cols = ["To Do", "Doing", "Done"]
            for col_name in cols:
                session.add(ColumnModel(name=col_name, board_id=new_board.id))
            
            await session.commit()

@app.get("/")
async def get_index():
    template_path = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
