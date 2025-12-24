from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import user_service
from app.models.user import User

router = APIRouter()

# --- ADMIN ENDPOINTS ---

@router.post("/", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Admin create user."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    return user_service.create_user(db, user_in)

@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Admin list users."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    return user_service.get_users(db, skip, limit)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Admin update user."""
    if current_user.role != 'admin':
         raise HTTPException(status_code=403, detail="Not authorized")
    return user_service.update_user(db, user_id, user_in)

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Admin delete user."""
    if current_user.role != 'admin':
         raise HTTPException(status_code=403, detail="Not authorized")
    return user_service.delete_user(db, user_id)

# --- MANAGER ENDPOINTS ---

@router.get("/team")
def get_my_team(
    current_user: User = Depends(deps.get_current_user)
):
    """Manager get team members."""
    # Manager, Admin, or maybe Project Manager?
    # Simple RBAC: admin or manager
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    return user_service.get_team(current_user.odoo_employee_id)
