from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
import os

from api.models_kanban import Board, Column, Task

router = APIRouter()

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "kanban.db"))
engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session

@router.get("/")
async def get_index():
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "kanban.html")
    with open(template_path, "r") as f:
        return HTMLResponse(f.read())

def format_task(task):
    return {"id": task.id, "title": task.title, "description": task.description, "tags": task.tags, "column_id": task.column_id}

def format_column(col):
    return {"id": col.id, "name": col.name, "tasks": [format_task(t) for t in col.tasks]}

def format_board(board):
    return {"id": board.id, "name": board.name, "columns": [format_column(c) for c in board.columns]}

@router.get("/api/board")
async def get_board(db: AsyncSession = Depends(get_db)):
    stmt = select(Board).options(selectinload(Board.columns).selectinload(Column.tasks)).limit(1)
    result = await db.execute(stmt)
    board = result.scalar_one_or_none()
    if not board:
        return {}
    return format_board(board)

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    tags: str = ""
    column_id: int

@router.post("/api/tasks")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(title=task.title, description=task.description, tags=task.tags, column_id=task.column_id)
    db.add(new_task)
    await db.commit()
    return {"status": "ok"}

class TaskMove(BaseModel):
    task_id: int
    column_id: int

@router.put("/api/tasks/move")
async def move_task(payload: TaskMove, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, payload.task_id)
    if task:
        task.column_id = payload.column_id
        await db.commit()
    return {"status": "ok"}
