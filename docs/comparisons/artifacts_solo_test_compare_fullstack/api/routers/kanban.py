from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional

from api.models_kanban import Board, Column, Task

router = APIRouter()

engine = create_async_engine("sqlite+aiosqlite:///kanban.db")
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None
    column_id: int

class TaskUpdate(BaseModel):
    column_id: int

class ColumnCreate(BaseModel):
    name: str
    board_id: int

@router.get("/api/board/{board_id}")
async def get_board(board_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Board).where(Board.id == board_id).options(
        selectinload(Board.columns).selectinload(Column.tasks)
    )
    result = await db.execute(stmt)
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    return {
        "id": board.id,
        "name": board.name,
        "columns": [
            {
                "id": col.id,
                "name": col.name,
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "tags": task.tags,
                        "column_id": task.column_id
                    }
                    for task in col.tasks
                ]
            }
            for col in board.columns
        ]
    }

@router.post("/api/tasks")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(title=task.title, description=task.description, tags=task.tags, column_id=task.column_id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return {"id": new_task.id}

@router.put("/api/tasks/{task_id}")
async def update_task_column(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    db_task = result.scalar_one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.column_id = task.column_id
    await db.commit()
    return {"status": "success"}

@router.post("/api/columns")
async def create_column(col: ColumnCreate, db: AsyncSession = Depends(get_db)):
    new_col = Column(name=col.name, board_id=col.board_id)
    db.add(new_col)
    await db.commit()
    await db.refresh(new_col)
    return {"id": new_col.id}
