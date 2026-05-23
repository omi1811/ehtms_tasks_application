from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base
import enum

class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    org_admin = "org_admin"
    manager = "manager"
    worker = "worker"

class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.worker, index=True) # UserRole is an enum that defines different user roles (e.g., admin, user)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True) # Foreign key to the Organization model
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=True, index= True) # Self-referential foreign key for manager-subordinate relationship
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


    # Relationships
    # For example, if you have a relationship with another model:
    # items = relationship("Item", back_populates="owner")
    tasks = relationship("Task", back_populates="author", foreign_keys="Task.author_id")
    assigned_tasks = relationship("Task", back_populates="assigned_to", foreign_keys="Task.assigned_to_id")
    subordinates = relationship("User", back_populates="manager", foreign_keys=[manager_id])
    manager = relationship(
        "User",
        back_populates="subordinates",
        foreign_keys=[manager_id],
        remote_side=[id],
    )
    organization = relationship("Organization", foreign_keys=[organization_id])
