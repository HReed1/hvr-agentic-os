import sys
import os
import asyncio
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.models_kanban import Base, Board, KanbanColumn
from api.routers.kanban import router

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kanban.db"))
SYNC_DB_URL = f"sqlite:///{DB_FILE}"

def seed_database():
    engine = create_engine(SYNC_DB_URL)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    if not session.query(Board).first():
        board = Board(name="Board 1")
        session.add(board)
        session.flush()
        c1 = KanbanColumn(name="To Do", board_id=board.id)
        c2 = KanbanColumn(name="Doing", board_id=board.id)
        c3 = KanbanColumn(name="Done", board_id=board.id)
        session.add_all([c1, c2, c3])
        session.commit()
    session.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_database()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def serve_kanban():
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api", "templates", "kanban.html"))
    with open(template_path, "r") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bin.launch_kanban:app", host="127.0.0.1", port=8000)