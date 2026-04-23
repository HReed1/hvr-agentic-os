import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from api.models_kanban import Base, Board, Column as DBColumn
from api.routers.kanban import router, engine, async_session

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as db:
        from sqlalchemy.future import select
        result = await db.execute(select(Board))
        board = result.scalars().first()
        if not board:
            board = Board(name="Board 1")
            db.add(board)
            await db.commit()
            await db.refresh(board)
            
            for c_name in ["To Do", "Doing", "Done"]:
                db.add(DBColumn(name=c_name, board_id=board.id))
            await db.commit()

@app.get("/")
async def index():
    template_path = os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
