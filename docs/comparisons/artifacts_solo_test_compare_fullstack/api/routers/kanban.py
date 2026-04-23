import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from api.models_kanban import Base, Board, KanbanColumn, Task

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "kanban.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

router = APIRouter(prefix="/api")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None
    column_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    column_id: Optional[int] = None

class ColumnCreate(BaseModel):
    name: str
    board_id: int

class BoardCreate(BaseModel):
    name: str

class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None
    column_id: int

class ColumnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    board_id: int
    tasks: List[TaskOut] = []

class BoardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    columns: List[ColumnOut] = []

@router.post("/boards", response_model=BoardOut)
async def create_board(board: BoardCreate, db: AsyncSession = Depends(get_db)):
    db_board = Board(name=board.name)
    db.add(db_board)
    await db.commit()
    await db.refresh(db_board)
    return db_board

@router.get("/boards/{board_id}", response_model=BoardOut)
async def get_board(board_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Board)
        .where(Board.id == board_id)
    )
    db_board = result.scalars().first()
    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found")
    return db_board

@router.get("/boards", response_model=List[BoardOut])
async def get_boards(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Board))
    return result.scalars().all()

@router.post("/columns", response_model=ColumnOut)
async def create_column(column: ColumnCreate, db: AsyncSession = Depends(get_db)):
    db_column = KanbanColumn(name=column.name, board_id=column.board_id)
    db.add(db_column)
    await db.commit()
    await db.refresh(db_column)
    return db_column

@router.post("/tasks", response_model=TaskOut)
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
    return db_task

@router.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    await db.commit()
    await db.refresh(db_task)
    return db_task
