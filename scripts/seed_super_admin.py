"""Seed script to create a super admin user."""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def seed_super_admin():
    engine = create_engine(settings.DATABASE_URL)
    
    with Session(engine) as db:
        # Check if super admin already exists
        existing = db.query(User).filter(User.email == "superuser@ehtms.com").first()
        if existing:
            existing.username = "superuser"
            existing.hashed_password = get_password_hash("March@2024")
            existing.role = UserRole.super_admin
            existing.is_active = True
            db.commit()
            print(f"Super admin already exists; credentials refreshed: {existing.email}")
            return
        
        # Create new super admin
        super_admin = User(
            email="superuser@ehtms.com",
            username="superuser",
            hashed_password=get_password_hash("March@2024"),  # Change in production!
            role=UserRole.super_admin,
            is_active=True
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print(f"Super admin created: {super_admin.email}")
        print(f"   Login: superuser@ehtms.com / March@2024")

if __name__ == "__main__":
    seed_super_admin()
