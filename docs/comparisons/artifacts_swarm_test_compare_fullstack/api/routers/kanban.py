import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from api.models_kanban import Base, Board, Column, Task

router = APIRouter(prefix="/api/kanban", tags=["kanban"])

DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///kanban.db")
engine = create_async_engine(DB_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    tags: Optional[str] = ""

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    column_id: Optional[int] = None

class ColumnCreate(BaseModel):
    name: str

class BoardCreate(BaseModel):
    name: str

@router.post("/boards")
async def create_board(data: BoardCreate, db: AsyncSession = Depends(get_db)):
    board = Board(name=data.name)
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return {"id": board.id, "name": board.name}

@router.get("/boards/{board_id}")
async def get_board(board_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Board).options(selectinload(Board.columns).selectinload(Column.tasks)).where(Board.id == board_id)
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
                    } for task in col.tasks
                ]
            } for col in board.columns
        ]
    }

@router.post("/boards/{board_id}/columns")
async def create_column(board_id: int, data: ColumnCreate, db: AsyncSession = Depends(get_db)):
    col = Column(name=data.name, board_id=board_id)
    db.add(col)
    await db.commit()
    await db.refresh(col)
    return {"id": col.id, "name": col.name, "board_id": col.board_id}

@router.post("/columns/{column_id}/tasks")
async def create_task(column_id: int, data: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(title=data.title, description=data.description, tags=data.tags, column_id=column_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {"id": task.id, "title": task.title, "column_id": task.column_id}

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
        
    await db.commit()
    await db.refresh(task)
    return {"id": task.id, "title": task.title, "column_id": task.column_id}

@router.get("/tasks/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "tags": task.tags,
        "column_id": task.column_id
    }