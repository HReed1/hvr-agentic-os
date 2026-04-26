import os
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from api.models_kanban import Board, KanbanColumn, Task

router = APIRouter(prefix="/api")

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "kanban.db"))
ASYNC_DB_URL = f"sqlite+aiosqlite:///{DB_FILE}"

engine = create_async_engine(ASYNC_DB_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

class TaskCreate(BaseModel):
    title: str
    description: str
    tags: str
    column_id: int

class TaskMove(BaseModel):
    column_id: int

class ColumnCreate(BaseModel):
    name: str
    board_id: int

@router.get("/board")
async def get_board_state(db: AsyncSession = Depends(get_db)):
    stmt = select(Board).options(selectinload(Board.columns).selectinload(KanbanColumn.tasks)).limit(1)
    result = await db.execute(stmt)
    board = result.scalars().first()
    if not board:
        return {}
    
    return {
        "id": board.id,
        "name": board.name,
        "columns": [
            {
                "id": c.id, 
                "name": c.name, 
                "tasks": [
                    {
                        "id": t.id, 
                        "title": t.title, 
                        "description": t.description, 
                        "tags": t.tags
                    } for t in c.tasks
                ]
            } for c in board.columns
        ]
    }

@router.post("/boards")
async def create_board(db: AsyncSession = Depends(get_db)):
    board = Board(name="New Board")
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return {"id": board.id}

@router.post("/columns")
async def create_column(col: ColumnCreate, db: AsyncSession = Depends(get_db)):
    new_col = KanbanColumn(name=col.name, board_id=col.board_id)
    db.add(new_col)
    await db.commit()
    await db.refresh(new_col)
    return {"id": new_col.id}

@router.get("/columns")
async def get_columns(board_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KanbanColumn).where(KanbanColumn.board_id == board_id))
    cols = result.scalars().all()
    return [{"id": c.id, "name": c.name} for c in cols]

@router.post("/tasks")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(
        title=task.title, 
        description=task.description, 
        tags=task.tags, 
        column_id=task.column_id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return {"id": new_task.id}

@router.get("/tasks/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()
    if not task:
        return {}
    return {"id": task.id, "title": task.title, "description": task.description, "tags": task.tags, "column_id": task.column_id}

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, task_move: TaskMove, db: AsyncSession = Depends(get_db)):
    await db.execute(update(Task).where(Task.id == task_id).values(column_id=task_move.column_id))
    await db.commit()
    return {"status": "ok"}