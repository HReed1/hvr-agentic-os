from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List

from api.models_kanban import Board, BoardColumn, Task
from api.database import get_db

router = APIRouter()

class TaskBase(BaseModel):
    title: str
    description: str
    tags: str

class TaskCreate(TaskBase):
    column_id: int

class TaskUpdate(BaseModel):
    column_id: int

class TaskResponse(TaskBase):
    id: int
    column_id: int
    class Config:
        from_attributes = True

class ColumnBase(BaseModel):
    name: str

class ColumnCreate(ColumnBase):
    board_id: int

class ColumnResponse(ColumnBase):
    id: int
    board_id: int
    tasks: List[TaskResponse] = []
    class Config:
        from_attributes = True

class BoardBase(BaseModel):
    name: str

class BoardResponse(BoardBase):
    id: int
    columns: List[ColumnResponse] = []
    class Config:
        from_attributes = True

@router.post("/boards/", response_model=BoardResponse)
async def create_board(board: BoardBase, db: AsyncSession = Depends(get_db)):
    db_board = Board(name=board.name)
    db.add(db_board)
    await db.commit()
    await db.refresh(db_board)
    return db_board

@router.get("/boards/{board_id}", response_model=BoardResponse)
async def get_board(board_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Board)
        .options(selectinload(Board.columns).selectinload(BoardColumn.tasks))
        .filter(Board.id == board_id)
    )
    board = result.scalars().first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.post("/columns/", response_model=ColumnResponse)
async def create_column(column: ColumnCreate, db: AsyncSession = Depends(get_db)):
    db_column = BoardColumn(name=column.name, board_id=column.board_id)
    db.add(db_column)
    await db.commit()
    await db.refresh(db_column)
    return db_column

@router.post("/tasks/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = Task(title=task.title, description=task.description, tags=task.tags, column_id=task.column_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.column_id = task.column_id
    await db.commit()
    await db.refresh(db_task)
    return db_task