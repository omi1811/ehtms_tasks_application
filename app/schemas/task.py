from pydantic import BaseModel
from datetime import datetime
from app.models.task import TaskStatus  # ← Import the Enum we defined

class TaskCreate(BaseModel):
    """What client sends when creating a task"""
    title: str
    description: str | None = None
    due_date: datetime | None = None

class TaskResponse(BaseModel):
    """What client receives after task operations"""
    id: int
    title: str
    description: str | None
    status: TaskStatus  # ← Enum: pending, in_progress, complete, archived
    due_date: datetime | None
    image_url: str | None
    completed_at: datetime | None
    created_at: datetime
    author_id: int  # ← Included in response (safe, not secret)
    
    class Config:
        from_attributes = True  # ← Allows SQLAlchemy → Pydantic conversion

class TaskComplete(BaseModel):
    """What client sends when marking task complete"""
    image_url: str  # ← Proof of completion