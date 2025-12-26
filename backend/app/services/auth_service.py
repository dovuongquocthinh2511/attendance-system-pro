from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import Optional

from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.token import TokenResponse
from app.core import security

class AuthService:
    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate user by email or phone and password.
        Returns User object if successful, None otherwise.
        """
        user = db.query(User).filter(
            or_(
                User.email == username,
                User.phone == username
            )
        ).first()
        
        if not user:
            return None
        if not security.verify_password(password, user.password_hash):
            return None
        return user

    def login(self, db: Session, username: str, password: str) -> TokenResponse:
        """
        Full login flow: authenticate and generate token.
        Raises HTTPException if authentication fails.
        """
        user = self.authenticate(db, username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/phone or password",
            )
        
        access_token = security.create_access_token(
            data={"sub": str(user.id), "role": user.role, "odoo_employee_id": user.odoo_employee_id}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role,
            "odoo_employee_id": user.odoo_employee_id
        }

    def logout(self, db: Session, token: str) -> None:
        """
        Invalidate token by adding to blacklist.
        """
        # Check if already blacklisted
        existing = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
        if not existing:
            db_token = TokenBlacklist(token=token)
            db.add(db_token)
            db.commit()

    def refresh_token(self, current_user: User) -> TokenResponse:
        """
        Generate new access token for current user.
        """
        access_token = security.create_access_token(
            data={"sub": str(current_user.id), "role": current_user.role, "odoo_employee_id": current_user.odoo_employee_id}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": current_user.role,
            "odoo_employee_id": current_user.odoo_employee_id
        }

auth_service = AuthService()
