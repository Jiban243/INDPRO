# backend/models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationship to cleanly fetch a user's tasks
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    # Every task has a stage restriction: Todo, In Progress, Done
    stage = Column(String, default="Todo", nullable=False) 
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship to find out who owns this task
    owner = relationship("User", back_populates="tasks")