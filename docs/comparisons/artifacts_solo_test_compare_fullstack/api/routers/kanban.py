from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from pydantic import BaseModel

from api.models_kanban import Board, ColumnModel, Task
from api.database import get_db

router = APIRouter()

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    tags: Optional[str] = ""
    column_id: int

class TaskUpdate(BaseModel):
    column_id: int

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
    return {"id": db_board.id, "name": db_board.name}

@router.get("/boards/{board_id}")
async def get_board(board_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Board)
        .where(Board.id == board_id)
        .options(selectinload(Board.columns).selectinload(ColumnModel.tasks))
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
    db_column = ColumnModel(name=column.name, board_id=column.board_id)
    db.add(db_column)
    await db.commit()
    await db.refresh(db_column)
    return {"id": db_column.id, "name": db_column.name, "board_id": db_column.board_id}

@router.post("/tasks")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = Task(title=task.title, description=task.description, tags=task.tags, column_id=task.column_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return {
        "id": db_task.id,
        "title": db_task.title,
        "description": db_task.description,
        "tags": db_task.tags,
        "column_id": db_task.column_id
    }

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.column_id = task_update.column_id
    await db.commit()
    return {"status": "success"}

@router.get("/tasks/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    db_task = result.scalars().first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": db_task.id,
        "title": db_task.title,
        "description": db_task.description,
        "tags": db_task.tags,
        "column_id": db_task.column_id
    }
