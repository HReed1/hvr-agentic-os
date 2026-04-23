from typing import List, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Board(Base):
    __tablename__ = 'boards'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    columns: Mapped[List["KanbanColumn"]] = relationship("KanbanColumn", back_populates="board", cascade="all, delete-orphan", lazy="selectin")

class KanbanColumn(Base):
    __tablename__ = 'columns'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id'))
    board: Mapped["Board"] = relationship("Board", back_populates="columns")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="column", cascade="all, delete-orphan", lazy="selectin")

class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    column_id: Mapped[int] = mapped_column(ForeignKey('columns.id'))
    column: Mapped["KanbanColumn"] = relationship("KanbanColumn", back_populates="tasks")
