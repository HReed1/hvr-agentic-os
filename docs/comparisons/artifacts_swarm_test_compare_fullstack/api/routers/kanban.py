import os
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from api.models_kanban import Board, Column, Task, get_db

router = APIRouter()

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    tags: str = ""
    column_id: int

class TaskUpdate(BaseModel):
    column_id: int

class ColumnCreate(BaseModel):
    name: str
    board_id: int

def serialize_task(t):
    return {"id": t.id, "title": t.title, "description": t.description, "tags": t.tags}

def serialize_column(c):
    return {"id": c.id, "name": c.name, "tasks": [serialize_task(t) for t in c.tasks]}

def serialize_board(b):
    return {"id": b.id, "name": b.name, "columns": [serialize_column(c) for c in b.columns]}

@router.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "kanban.html")
    with open(template_path, "r") as f:
        return f.read()

@router.get("/api/state")
async def get_state(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Board).options(selectinload(Board.columns).selectinload(Column.tasks))
    )
    boards = result.scalars().all()
    return [serialize_board(b) for b in boards]

@router.post("/api/tasks")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(title=task.title, description=task.description, tags=task.tags, column_id=task.column_id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return serialize_task(new_task)

@router.put("/api/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    t = result.scalars().first()
    if t:
        t.column_id = task.column_id
        await db.commit()
    return {"status": "ok"}

@router.post("/api/columns")
async def create_column(col: ColumnCreate, db: AsyncSession = Depends(get_db)):
    new_col = Column(name=col.name, board_id=col.board_id)
    db.add(new_col)
    await db.commit()
    await db.refresh(new_col)
    return {"id": new_col.id, "name": new_col.name}