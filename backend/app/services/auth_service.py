from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import Optional

from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.token import TokenResponse
from app.core import security
from app.models.password_reset import PasswordResetToken
from app.services.email_service import email_service
import secrets
from datetime import datetime, timedelta

class AuthService:
    def forgot_password(self, db: Session, email: str):
        # 1. Check if user exists
        from app.core.logger import logger
        logger.info(f"--- FGO Password Request for: {email} ---")
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.warning(f"--- User NOT FOUND in DB: {email} ---")
            # Security: Don't reveal if user exists. Just return Success.
            return 
        
        logger.info(f"--- User FOUND: {user.email} (ID: {user.id}) ---") 
        
        # 2. Generate OTP
        otp = secrets.token_hex(3).upper() # 6 chars
        expires = datetime.now() + timedelta(minutes=10)
        
        # 3. Save to DB
        reset_token = PasswordResetToken(
            email=email,
            otp=otp,
            expires_at=expires,
            is_used=False
        )
        db.add(reset_token)
        db.commit()
        
        # 4. Send Email
        email_service.send_otp(email, otp)

    def reset_password(self, db: Session, email: str, otp: str, new_password: str):
        # 1. Find valid OTP
        token = db.query(PasswordResetToken).filter(
            PasswordResetToken.email == email,
            PasswordResetToken.otp == otp,
            PasswordResetToken.is_used == False,
            PasswordResetToken.expires_at > datetime.now()
        ).first()
        
        if not token:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
            
        # 2. Find User
        user = db.query(User).filter(User.email == email).first()
        if not user:
             raise HTTPException(status_code=404, detail="User not found")

        # 3. Update Password
        user.password_hash = security.hash_password(new_password)
        
        # 4. Invalidate Token
        token.is_used = True
        
        db.commit()


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
