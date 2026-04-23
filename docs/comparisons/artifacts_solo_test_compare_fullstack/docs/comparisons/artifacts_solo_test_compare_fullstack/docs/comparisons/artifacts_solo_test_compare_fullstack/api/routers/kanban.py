import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional

from api.models_kanban import Board, Column as DBColumn, Task

router = APIRouter()

DB_URL = "sqlite+aiosqlite:///kanban.db"
engine = create_async_engine(DB_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session

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

@router.get("/api/board")
async def get_board(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Board).options(selectinload(Board.columns).selectinload(DBColumn.tasks)))
    board = result.scalars().first()
    if not board:
        return {"error": "No board found"}
    
    cols = []
    for col in board.columns:
        tsks = []
        for task in col.tasks:
            tsks.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "tags": task.tags,
                "column_id": task.column_id
            })
        cols.append({
            "id": col.id,
            "name": col.name,
            "tasks": tsks
        })
        
    return {
        "id": board.id,
        "name": board.name,
        "columns": cols
    }

@router.post("/api/tasks")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(**task.model_dump())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

@router.put("/api/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)
        
    await db.commit()
    return {"status": "ok"}
    
@router.post("/api/columns")
async def create_column(col: ColumnCreate, db: AsyncSession = Depends(get_db)):
    new_col = DBColumn(**col.model_dump())
    db.add(new_col)
    await db.commit()
    await db.refresh(new_col)
    return new_col
