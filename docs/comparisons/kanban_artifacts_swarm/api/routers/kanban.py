from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
from api.models_kanban import Board, Column, Task

router = APIRouter(prefix="/api/v1")

# Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None
    column_id: int
    order: int = 0

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    column_id: Optional[int] = None
    order: Optional[int] = None

class TaskSchema(TaskBase):
    id: int
    class Config:
        from_attributes = True

class ColumnBase(BaseModel):
    name: str
    board_id: int
    order: int = 0

class ColumnCreate(ColumnBase):
    pass

class ColumnSchema(ColumnBase):
    id: int
    tasks: List[TaskSchema]
    class Config:
        from_attributes = True

class BoardBase(BaseModel):
    name: str

class BoardCreate(BoardBase):
    pass

class BoardSchema(BoardBase):
    id: int
    columns: List[ColumnSchema]
    class Config:
        from_attributes = True

# Dependency placeholder (to be overridden in app/tests)
async def get_db():
    raise NotImplementedError

@router.post("/boards", response_model=BoardSchema)
async def create_board(board: BoardCreate, db: AsyncSession = Depends(get_db)):
    db_board = Board(name=board.name)
    db.add(db_board)
    await db.commit()
    await db.refresh(db_board)
    return db_board

@router.get("/boards/{board_id}", response_model=BoardSchema)
async def get_board(board_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Board)
        .where(Board.id == board_id)
        .options(selectinload(Board.columns).selectinload(Column.tasks))
    )
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.post("/columns", response_model=ColumnSchema)
async def create_column(column: ColumnCreate, db: AsyncSession = Depends(get_db)):
    db_column = Column(**column.model_dump())
    db.add(db_column)
    await db.commit()
    await db.refresh(db_column)
    # Return with empty tasks list
    return ColumnSchema(
        id=db_column.id,
        name=db_column.name,
        board_id=db_column.board_id,
        order=db_column.order,
        tasks=[]
    )

@router.post("/tasks", response_model=TaskSchema)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = Task(**task.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.patch("/tasks/{task_id}", response_model=TaskSchema)
async def update_task(task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    db_task = result.scalar_one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    await db.commit()
    await db.refresh(db_task)
    return db_task
