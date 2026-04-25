from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from pydantic import BaseModel
from api.models_kanban import Board, BoardColumn, Task
from api.database import get_db

router = APIRouter(prefix="/api/kanban")

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    tags: str = ""
    column_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    column_id: Optional[int] = None

class ColumnCreate(BaseModel):
    name: str
    board_id: int

def task_to_dict(t: Task) -> dict:
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "tags": t.tags,
        "column_id": t.column_id
    }

def column_to_dict(c: BoardColumn) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "tasks": [task_to_dict(t) for t in c.tasks]
    }

def board_to_dict(board: Board) -> dict:
    return {
        "id": board.id,
        "name": board.name,
        "columns": [column_to_dict(c) for c in board.columns]
    }

@router.get("/boards")
async def get_boards(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Board))
    boards = result.scalars().all()
    return [{"id": b.id, "name": b.name} for b in boards]

@router.get("/boards/{board_id}")
async def get_board(board_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Board).where(Board.id == board_id).options(
        selectinload(Board.columns).selectinload(BoardColumn.tasks)
    )
    result = await db.execute(query)
    board = result.scalars().first()
    if not board:
        return {"error": "not found"}
    return board_to_dict(board)

@router.post("/columns")
async def create_column(col: ColumnCreate, db: AsyncSession = Depends(get_db)):
    db_col = BoardColumn(name=col.name, board_id=col.board_id)
    db.add(db_col)
    await db.commit()
    await db.refresh(db_col)
    return {"id": db_col.id, "name": db_col.name}

@router.post("/tasks")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = Task(
        title=task.title,
        description=task.description,
        tags=task.tags,
        column_id=task.column_id
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return {"id": db_task.id}

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    db_task = result.scalars().first()
    if not db_task:
        return {"error": "not found"}
    
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    await db.commit()
    return {"status": "ok"}