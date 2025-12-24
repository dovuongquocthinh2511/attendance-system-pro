from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional, Dict
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core import security
from app.services.odoo_client import odoo_client

class UserService:
    def create_user(self, db: Session, user_in: UserCreate) -> User:
        """
        Create a new user.
        Checks for existing email/phone.
        Hashes password.
        """
        # Check if email exists
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check if phone exists (if provided)
        if user_in.phone and db.query(User).filter(User.phone == user_in.phone).first():
            raise HTTPException(status_code=400, detail="Phone number already registered")

        # Create user object
        user = User(
            email=user_in.email,
            phone=user_in.phone,
            password_hash=security.hash_password(user_in.password),
            role=user_in.role,
            odoo_employee_id=user_in.odoo_employee_id,
            is_active=user_in.is_active
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def update_user(self, db: Session, user_id: int, user_in: UserUpdate) -> User:
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        update_data = user_in.dict(exclude_unset=True)
        if 'password' in update_data:
            hashed_password = security.hash_password(update_data['password'])
            update_data['password_hash'] = hashed_password
            del update_data['password']

        for field, value in update_data.items():
            setattr(user, field, value)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def delete_user(self, db: Session, user_id: int) -> User:
        user = self.get_user_by_id(db, user_id)
        if not user:
             raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
        return user

    def get_team(self, manager_employee_id: int) -> List[Dict]:
        """
        Get team members from Odoo (direct reports).
        """
        # Search employees where parent_id = manager_employee_id
        domain = [['parent_id', '=', manager_employee_id]]
        fields = ['id', 'name', 'job_title', 'work_email', 'mobile_phone']
        return odoo_client.search_read('hr.employee', domain, fields)

user_service = UserService()
