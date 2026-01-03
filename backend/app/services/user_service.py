from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional, Dict
from app.models.user import User
from app.schemas.user import UserCreateRequest, UserUpdateRequest
from app.core import security
from app.services.odoo_client import odoo_client
from app.services.employee_service import employee_service

class UserService:

    def create_user(self, db: Session, user_in: UserCreateRequest) -> User:
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

        odoo_employee_id = user_in.odoo_employee_id
        
        # Auto-link with Odoo Employee if not provided
        if not odoo_employee_id:
            odoo_employee_id = employee_service.find_by_email_or_phone(user_in.email, user_in.phone)

        # Create user object
        user = User(
            email=user_in.email,
            phone=user_in.phone,
            password_hash=security.hash_password(user_in.password),
            role=user_in.role,
            odoo_employee_id=odoo_employee_id,
            is_active=user_in.is_active
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def update_user(self, db: Session, user_id: int, user_in: UserUpdateRequest, allow_auto_link: bool = False) -> User:
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        update_data = user_in.dict(exclude_unset=True)
        
        # Auto-link logic on Email or Phone change
        # Only triggered if allow_auto_link is True
        if allow_auto_link and 'odoo_employee_id' not in update_data:
            new_email = update_data.get('email')
            new_phone = update_data.get('phone')
            
            # Use new values if changed, else use existing values
            final_email = new_email if new_email is not None else user.email
            final_phone = new_phone if new_phone is not None else user.phone
            
            # Only re-sync if one of them actually changed
            if new_email is not None or new_phone is not None:
                found_id = employee_service.find_by_email_or_phone(final_email, final_phone)
                # If found, update. If not found, set to None (unlink).
                update_data['odoo_employee_id'] = found_id

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
