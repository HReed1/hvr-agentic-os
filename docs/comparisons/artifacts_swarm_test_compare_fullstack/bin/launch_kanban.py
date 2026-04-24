import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from api.routers.kanban import router
from api.models_kanban import engine, Base, Board, Column, AsyncSessionLocal

app = FastAPI()
app.include_router(router)

async def seed_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy.future import select
        res = await session.execute(select(Board))
        if not res.scalars().first():
            b = Board(name="Board 1")
            session.add(b)
            await session.flush()
            session.add(Column(name="To Do", board_id=b.id))
            session.add(Column(name="Doing", board_id=b.id))
            session.add(Column(name="Done", board_id=b.id))
            await session.commit()

@app.on_event("startup")
async def startup_event():
    await seed_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)