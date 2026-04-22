from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from pydantic import BaseModel

from api.models_kanban import Board, Column, Task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

router = APIRouter()

engine = create_async_engine("sqlite+aiosqlite:///./kanban.db", echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    tags: str = ""
    column_id: int

class TaskUpdate(BaseModel):
    column_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None

class ColumnCreate(BaseModel):
    name: str
    board_id: int

class BoardCreate(BaseModel):
    name: str

@router.post("/boards")
async def create_board(board: BoardCreate, db: AsyncSession = Depends(get_db)):
    db_board = Board(name=board.name)
    db.add(db_board)
    await db.commit()
    await db.refresh(db_board)
    return db_board

@router.get("/boards/{board_id}")
async def get_board(board_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Board).where(Board.id == board_id).options(
            selectinload(Board.columns).selectinload(Column.tasks)
        )
    )
    board = result.scalars().first()
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

@router.post("/columns")
async def create_column(column: ColumnCreate, db: AsyncSession = Depends(get_db)):
    db_col = Column(name=column.name, board_id=column.board_id)
    db.add(db_col)
    await db.commit()
    await db.refresh(db_col)
    return {"id": db_col.id, "name": db_col.name, "board_id": db_col.board_id}

@router.post("/tasks")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = Task(title=task.title, description=task.description, tags=task.tags, column_id=task.column_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return {"id": db_task.id, "title": db_task.title, "column_id": db_task.column_id}

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    await db.commit()
    return {"id": db_task.id, "column_id": db_task.column_id}

@router.get("/tasks/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": db_task.id, "title": db_task.title, "description": db_task.description, "tags": db_task.tags, "column_id": db_task.column_id}
