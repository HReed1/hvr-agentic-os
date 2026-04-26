from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Board(Base):
    __tablename__ = "boards"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    columns = relationship("KanbanColumn", back_populates="board", cascade="all, delete-orphan", lazy="selectin")

class KanbanColumn(Base):
    __tablename__ = "columns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"))
    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan", lazy="selectin")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    tags = Column(String)
    column_id = Column(Integer, ForeignKey("columns.id"))
    column = relationship("KanbanColumn", back_populates="tasks")