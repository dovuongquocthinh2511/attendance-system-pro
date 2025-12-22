from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.schemas.user import UserCreate
from app.core import security

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

user_service = UserService()
