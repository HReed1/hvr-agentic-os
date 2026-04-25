from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
from api.db_deps import get_db
from api.models_kanban import Board, Column, Task

router = APIRouter(prefix="/api")

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None
    column_id: int

class TaskUpdate(BaseModel):
    column_id: Optional[int] = None

class ColumnCreate(BaseModel):
    name: str
    board_id: int

@router.get("/board")
async def get_board(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Board).options(
            selectinload(Board.columns).selectinload(Column.tasks)
        )
    )
    board = result.scalars().first()
    if not board:
        raise HTTPException(status_code=404, detail="No board found")
    return board

@router.post("/columns")
async def create_column(col: ColumnCreate, db: AsyncSession = Depends(get_db)):
    new_col = Column(name=col.name, board_id=col.board_id)
    db.add(new_col)
    await db.commit()
    await db.refresh(new_col)
    return new_col

@router.post("/tasks")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(
        title=task.title,
        description=task.description,
        tags=task.tags,
        column_id=task.column_id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

@router.patch("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Task).where(Task.id == task_id))
    db_task = res.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.column_id is not None:
        db_task.column_id = task.column_id
    await db.commit()
    await db.refresh(db_task)
    return db_task
