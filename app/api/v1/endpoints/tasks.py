import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.task import Task, TaskStatus
from app.services.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

# ─────────────────────────────────────
# PYDANTIC SCHEMAS
# ─────────────────────────────────────
class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    assigned_to_email: str

class PhotoUpload(BaseModel):
    task_id: int

# ─────────────────────────────────────
# DEPENDENCIES
# ────────────────────────────────────
def require_assigner(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.org_admin, UserRole.manager]:
        raise HTTPException(403, detail="Only admins/managers can assign tasks.")
    return current_user

def require_worker(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.worker:
        raise HTTPException(403, detail="Only workers can upload photo proof.")
    return current_user

# ─────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────
@router.post("/assign", status_code=201)
def assign_task(
    data: TaskCreate,
    current_user: User = Depends(require_assigner),
    db: Session = Depends(get_db)
):
    """Assign a task to a worker in the same organization"""
    worker = db.query(User).filter(
        User.email == data.assigned_to_email,
        User.organization_id == current_user.organization_id
    ).first()
    if not worker or worker.role != UserRole.worker:
        raise HTTPException(404, detail="Worker not found in your organization.")
        
    task = Task(
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        status=TaskStatus.pending,
        author_id=current_user.id,
        assigned_to_id=worker.id,
        assigned_by_id=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"message": "Task assigned", "task_id": task.id, "assigned_to": worker.email}

@router.post("/upload-proof", status_code=200)
async def upload_task_proof(
    file: UploadFile = File(...),
    task_id: int = None,
    current_user: User = Depends(require_worker),
    db: Session = Depends(get_db)
):
    """Worker uploads photo proof to complete a task"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.assigned_to_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(404, detail="Task not found or not assigned to you.")
    if task.status == TaskStatus.complete:
        raise HTTPException(400, detail="Task already completed.")
        
    # Save locally (MinIO integration added during deployment)
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    safe_name = f"{task_id}_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    upload_dir = "uploads/tasks"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, safe_name)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    task.image_url = f"/{upload_dir}/{safe_name}"
    task.status = TaskStatus.complete
    task.completed_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Photo uploaded. Task marked complete.", "file_url": task.image_url}