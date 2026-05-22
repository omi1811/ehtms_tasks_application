from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskResponse, TaskComplete
from app.services.database import get_db
from app.api.v1.endpoints.auth import get_current_user  # ← Import the bouncer
from app.models.user import User
from sqlalchemy import func, case
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
    task.completed_at = datetime.now(timezone.utc)
    
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

@router.get("/tasks/calendar", response_model=list[TaskResponse])
def get_calendar_tasks(
    start_date: str,
    end_date: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        start_dt = datetime.strptime(start_date, "%d-%m-%Y")
        end_dt = datetime.strptime(end_date, "%d-%m-%Y")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use DD-MM-YYYY.")
    
    return(
        db.query(Task)
        .filter(
            Task.author_id == current_user.id,
            Task.due_date.between(start_dt, end_dt),
            Task.status != TaskStatus.archived
        )
        .order_by(Task.due_date.asc())
        .all()
    )

@router.get("/tasks/stats")
def get_task_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)
    stats = db.query(
        func.count(case((Task.status == TaskStatus.pending, 1))).label("pending"),
        func.count(case((Task.status == TaskStatus.in_progress, 1))).label("in_progress"),
        func.count(case((Task.status == TaskStatus.complete, 1))).label("complete"),
        func.count(case((Task.status == TaskStatus.archived, 1))).label("archived"),
        func.count(Task.id).label("total")
    ).filter(
        Task.author_id == current_user.id,
        Task.created_at >= month_start,
        Task.created_at <= month_end
    ).first()
    
    return {
        "pending": stats.pending,
        "in_progress": stats.in_progress,
        "complete": stats.complete,
        "archived": stats.archived,
        "total": stats.total,
        "period": f"{month_start.strftime('%B-%Y')} to {month_end.strftime('%B-%Y')}"
    }

@router.get("/tasks/memory", response_model=list[TaskResponse])
def get_task_memory(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Task)
        .filter(
            Task.author_id == current_user.id,
            Task.status.in_([TaskStatus.complete, TaskStatus.archived])
        )
        .order_by(Task.completed_at.desc(), Task.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
