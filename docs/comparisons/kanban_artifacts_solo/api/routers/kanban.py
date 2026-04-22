from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.models_kanban import Board, Column, Task

router = APIRouter()

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    tags: Optional[str] = ""
    column_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    column_id: Optional[int] = None

class ColumnCreate(BaseModel):
    name: str
    board_id: int

def get_db(): ...

@router.get("/boards/{board_id}")
async def get_board(board_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    columns_data = []
    for col in board.columns:
        tasks_data = [{"id": t.id, "title": t.title, "description": t.description, "tags": t.tags, "column_id": t.column_id} for t in col.tasks]
        columns_data.append({"id": col.id, "name": col.name, "tasks": tasks_data})
        
    return {"id": board.id, "name": board.name, "columns": columns_data}

@router.post("/tasks")
async def create_task(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(title=task_in.title, description=task_in.description, tags=task_in.tags, column_id=task_in.column_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {"id": task.id, "title": task.title, "column_id": task.column_id}

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, task_in: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_in.model_dump(exclude_unset=True) if hasattr(task_in, "model_dump") else task_in.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(task, k, v)
        
    await db.commit()
    await db.refresh(task)
    return {"id": task.id, "title": task.title, "column_id": task.column_id, "description": task.description, "tags": task.tags}

@router.post("/columns")
async def create_column(col_in: ColumnCreate, db: AsyncSession = Depends(get_db)):
    col = Column(name=col_in.name, board_id=col_in.board_id)
    db.add(col)
    await db.commit()
    await db.refresh(col)
    return {"id": col.id, "name": col.name}
