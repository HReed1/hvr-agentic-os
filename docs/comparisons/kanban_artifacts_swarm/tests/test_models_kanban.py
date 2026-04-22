import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from api.models_kanban import Base, Board, Column, Task
from sqlalchemy import select

@pytest_asyncio.fixture(loop_scope="function")
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session() as session:
        yield session
        
    await engine.dispose()

@pytest.mark.asyncio
async def test_kanban_models_creation(async_session):
    # Create Board
    board = Board(name="Project Alpha")
    async_session.add(board)
    await async_session.commit()
    await async_session.refresh(board)
    
    # Create Column
    col = Column(name="To Do", board_id=board.id)
    async_session.add(col)
    await async_session.commit()
    await async_session.refresh(col)
    
    # Create Task
    task = Task(title="Initial Task", description="Testing", tags="urgent,dev", column_id=col.id)
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    
    assert board.id is not None
    assert col.board_id == board.id
    assert task.column_id == col.id
    assert task.tags == "urgent,dev"

@pytest.mark.asyncio
async def test_kanban_relationship_integrity(async_session):
    board = Board(name="B1")
    async_session.add(board)
    await async_session.commit()
    
    col = Column(name="C1", board_id=board.id)
    async_session.add(col)
    await async_session.commit()
    
    # Verify Column exists in database linked to Board
    stmt = select(Column).where(Column.board_id == board.id)
    result = await async_session.execute(stmt)
    fetched_col = result.scalar_one()
    assert fetched_col.name == "C1"
