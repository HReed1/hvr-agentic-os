from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from api.models_kanban import Board, Column, Task

async def get_db():
    raise NotImplementedError("Dependency not overridden")

router = APIRouter(prefix="/api/kanban", tags=["kanban"])

@router.post("/boards", response_model=None)
async def create_board(name: str, db=Depends(get_db)):
    board = Board(name=name)
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board

@router.get("/boards/{board_id}", response_model=None)
async def get_board_state(board_id: int, db=Depends(get_db)):
    stmt = select(Board).where(Board.id == board_id).options(
        selectinload(Board.columns).selectinload(Column.tasks)
    )
    result = await db.execute(stmt)
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.post("/boards/{board_id}/columns", response_model=None)
async def create_column(board_id: int, name: str, db=Depends(get_db)):
    col = Column(name=name, board_id=board_id)
    db.add(col)
    await db.commit()
    await db.refresh(col)
    return col

@router.post("/columns/{column_id}/tasks", response_model=None)
async def create_task(column_id: int, title: str, description: str, tags: str, db=Depends(get_db)):
    task = Task(title=title, description=description, tags=tags, column_id=column_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.patch("/tasks/{task_id}", response_model=None)
async def update_task(task_id: int, column_id: int, db=Depends(get_db)):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.column_id = column_id
    await db.commit()
    await db.refresh(task)
    return task

@router.get("/tasks/{task_id}", response_model=None)
async def get_task(task_id: int, db=Depends(get_db)):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
