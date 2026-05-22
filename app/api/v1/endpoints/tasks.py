from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskResponse, TaskComplete
from app.services.database import get_db
from app.api.v1.endpoints.auth import get_current_user  # ← Import the bouncer
from app.models.user import User

router = APIRouter()

# CREATE TASK (Auto-injects author_id from JWT)
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),  # ← Bouncer verifies token
    db: Session = Depends(get_db)
):
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        status=TaskStatus.pending,  # ← Default status
        author_id=current_user.id    # ← 🔒 Auto-set from token (no manual input)
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)  # ← Fetches auto-generated ID
    return new_task

#GET MY TASKS (Only returns tasks owned by current_user)
@router.get("/tasks", response_model=list[TaskResponse])
def get_my_tasks(
    skip: int = 0,
    limit: int = 20,
    status_filter: TaskStatus | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter(Task.author_id == current_user.id)
    
    # Optional: Filter by status (e.g., ?status_filter=pending)
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    # Pagination: skip/limit
    tasks = query.offset(skip).limit(limit).all()
    return tasks

# MARK TASK COMPLETE (With photo proof)
@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    complete_data: TaskComplete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Find task AND verify ownership in one query
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.author_id == current_user.id  # ← 🔒 Only owner can modify
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )
    
    # 2. Update task
    task.status = TaskStatus.complete
    task.image_url = complete_data.image_url
    task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    return task

# ARCHIVE TASK (Move to memory)
@router.patch("/tasks/{task_id}/archive", response_model=TaskResponse)
def archive_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.author_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or unauthorized"
        )
    
    task.status = TaskStatus.archived
    db.commit()
    db.refresh(task)
    return task