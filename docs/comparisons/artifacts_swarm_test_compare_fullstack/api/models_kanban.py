import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

DATABASE_URL = "sqlite+aiosqlite:///kanban.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

class Board(Base):
    __tablename__ = 'boards'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    columns = relationship("Column", back_populates="board", cascade="all, delete-orphan")

class Column(Base):
    __tablename__ = 'columns'
    id: Mapped[int] = mapped_column(primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id'))
    name: Mapped[str] = mapped_column()
    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    column_id: Mapped[int] = mapped_column(ForeignKey('columns.id'))
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    tags: Mapped[str] = mapped_column()
    column = relationship("Column", back_populates="tasks")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session