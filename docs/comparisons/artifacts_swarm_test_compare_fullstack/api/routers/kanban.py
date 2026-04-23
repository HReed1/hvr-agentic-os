from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from api.models_kanban import Board, Column, Task, get_db

router = APIRouter(prefix="/api/kanban")

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
async def create_board(board: BoardCreate, db: AsyncSession = Depends(get_db)):
    new_board = Board(name=board.name)
    db.add(new_board)
    await db.commit()
    await db.refresh(new_board)
    return {"id": new_board.id, "name": new_board.name}

@router.post("/boards/{board_id}/columns")
async def create_column(board_id: int, col: ColumnCreate, db: AsyncSession = Depends(get_db)):
    new_col = Column(name=col.name, board_id=board_id)
    db.add(new_col)
    await db.commit()
    await db.refresh(new_col)
    return {"id": new_col.id, "name": new_col.name}

@router.post("/columns/{column_id}/tasks")
async def create_task(column_id: int, task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(title=task.title, description=task.description, tags=task.tags, column_id=column_id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return {"id": new_task.id, "title": new_task.title}

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, task_upd: TaskUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Task).where(Task.id == task_id))
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.title = task_upd.title if task_upd.title is not None else task.title
    task.description = task_upd.description if task_upd.description is not None else task.description
    task.tags = task_upd.tags if task_upd.tags is not None else task.tags
    task.column_id = task_upd.column_id if task_upd.column_id is not None else task.column_id
    
    await db.commit()
    return {"status": "ok"}

@router.get("/boards/{board_id}/state")
async def get_board_state(board_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Board).where(Board.id == board_id))
    board = res.scalar_one_or_none()
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
