from sqlalchemy import Column as SAColumn, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Board(Base):
    __tablename__ = 'boards'
    id = SAColumn(Integer, primary_key=True, index=True)
    name = SAColumn(String, index=True)
    columns = relationship("Column", back_populates="board", cascade="all, delete-orphan")

class Column(Base):
    __tablename__ = 'columns'
    id = SAColumn(Integer, primary_key=True, index=True)
    name = SAColumn(String, index=True)
    board_id = SAColumn(Integer, ForeignKey('boards.id'))
    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = 'tasks'
    id = SAColumn(Integer, primary_key=True, index=True)
    title = SAColumn(String, index=True)
    description = SAColumn(String)
    tags = SAColumn(String)
    column_id = SAColumn(Integer, ForeignKey('columns.id'))
    column = relationship("Column", back_populates="tasks")
