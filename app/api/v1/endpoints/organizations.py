from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.services.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from pydantic import BaseModel
from app.core.security import get_password_hash

router = APIRouter()

class OrgCreate(BaseModel):
    name: str

def require_super_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can manage organizations."
        )
    return current_user

@router.post("/org", status_code=201)
def create_organization(
    org: OrgCreate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new organization (super_admin only)"""
    # Check if org name already exists
    existing = db.query(Organization).filter(Organization.name == org.name).first()
    if existing:
        raise HTTPException(400, detail="Organization name already exists.")
    
    new_org = Organization(name=org.name, created_by_super_admin_id=current_user.id)
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    return {"message": "Organization created", "id": new_org.id, "name": new_org.name}

class AssignOrgAdmin(BaseModel):
    user_email: str

@router.post("/org/{org_id}/assign-admin")
def assign_org_admin(
    org_id: int,
    data: AssignOrgAdmin,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Assign org_admin role to a user (super_admin only)"""
    # 1. Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, detail="Organization not found.")
    
    # 2. Find user by email
    user = db.query(User).filter(User.email == data.user_email).first()
    if not user:
        raise HTTPException(404, detail="User not found.")
    
    # 3. Assign organization and role
    user.organization_id = org_id
    user.role = UserRole.org_admin
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {user.email} is now org_admin of {org.name}",
        "user_id": user.id,
        "organization_id": org_id
    }

class WorkerCreate(BaseModel):
    email: str
    username: str
    password: str

def require_org_manager(current_user: User = Depends(get_current_user)):
    """Dependency: Only org_admin or manager can proceed"""
    if current_user.role not in [UserRole.org_admin, UserRole.manager]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Organization Admins or Managers can create workers."
        )
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must belong to an organization to manage users."
        )
    return current_user

@router.post("/org/{org_id}/workers", status_code=201)
def create_worker(
    org_id: int,
    worker: WorkerCreate,
    current_user: User = Depends(require_org_manager),
    db: Session = Depends(get_db)
):
    """Create a worker (org_admin or manager only)"""
    # 1. Enforce organization scope
    if current_user.organization_id != org_id:
        raise HTTPException(403, detail="You can only create workers in your own organization.")
    
    # 2. Check for duplicates
    if db.query(User).filter(User.email == worker.email).first():
        raise HTTPException(400, detail="Email already registered.")
    if db.query(User).filter(User.username == worker.username).first():
        raise HTTPException(400, detail="Username already taken.")
        
    # 3. Create worker (role is HARD LOCKED to 'worker')
    new_worker = User(
        email=worker.email,
        username=worker.username,
        hashed_password=get_password_hash(worker.password),
        role=UserRole.worker,  # 🔒 Security: Cannot self-assign higher roles
        organization_id=org_id,
        is_active=True
    )
    
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)
    
    return {
        "message": "Worker created successfully",
        "user_id": new_worker.id,
        "email": new_worker.email,
        "organization_id": new_worker.organization_id
    }

class ManagerCreate(BaseModel):
    email: str
    username: str
    password: str
    manager_id: int | None = None  # Optional: Assign to a higher-level manager (PM → GM, etc.)

@router.post("/org/{org_id}/managers", status_code=201)
def create_manager(
    org_id: int,
    data: ManagerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new manager or promote an existing worker (org_admin only)"""
    # 1. Role & Scope Guards
    if current_user.role != UserRole.org_admin:
        raise HTTPException(403, detail="Only Organization Admins can create managers.")
    if current_user.organization_id != org_id:
        raise HTTPException(403, detail="Scope mismatch. You can only manage your own org.")
        
    # 2. Validate optional manager_id (if provided)
    if data.manager_id:
        parent = db.query(User).filter(
            User.id == data.manager_id, 
            User.organization_id == org_id
        ).first()
        if not parent or parent.role not in [UserRole.org_admin, UserRole.manager]:
            raise HTTPException(400, detail="Invalid manager_id. Must be an org_admin or manager in your org.")

    # 3. Check if user already exists (Promotion flow)
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        if existing_user.organization_id != org_id:
            raise HTTPException(400, detail="User belongs to another organization.")
            
        existing_user.role = UserRole.manager
        existing_user.manager_id = data.manager_id
        db.commit()
        db.refresh(existing_user)
        return {"message": "User promoted to Manager", "user_id": existing_user.id, "role": existing_user.role}

    # 4. Create new manager (Creation flow)
    new_manager = User(
        email=data.email,
        username=data.username,
        hashed_password=get_password_hash(data.password),
        role=UserRole.manager,
        organization_id=org_id,
        manager_id=data.manager_id,
        is_active=True
    )
    db.add(new_manager)
    db.commit()
    db.refresh(new_manager)
    
    return {"message": "Manager created", "user_id": new_manager.id, "email": new_manager.email}