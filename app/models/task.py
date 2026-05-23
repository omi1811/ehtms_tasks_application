from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base
import enum

class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    archived = "archived"

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    image_url = Column(String(500), nullable=True)
    status = Column(SQLAEnum(TaskStatus), default=TaskStatus.pending)
    author_id = Column(Integer, ForeignKey('users.id')) # Foreign key to the User model
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True) # Foreign key to the User model for task assignment
    assigned_by_id = Column(Integer, ForeignKey('users.id'), nullable=True) # Foreign key to the User model for task assignment
    # Relationships
    author = relationship("User", back_populates="tasks", foreign_keys=[author_id])
    assigned_to = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
