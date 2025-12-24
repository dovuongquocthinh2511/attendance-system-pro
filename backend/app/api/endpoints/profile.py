from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any
from app.api import deps
from app.models.user import User
from app.services.profile_service import profile_service

router = APIRouter()

@router.get("/")
def get_my_profile(current_user: User = Depends(deps.get_current_user)):
    """Get current user's Odoo profile."""
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    return profile_service.get_profile(current_user.odoo_employee_id)

@router.put("/")
def update_my_profile(
    updates: Dict[str, Any] = Body(...),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update current user's profile.
    Allowed keys: mobile_phone, work_email, identification_id, birthday.
    """
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    try:
        success = profile_service.update_profile(current_user.odoo_employee_id, updates)
        if success:
             return {"msg": "Profile updated successfully"}
        return {"msg": "No changes made or invalid fields"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/contract")
def get_my_contract(current_user: User = Depends(deps.get_current_user)):
    """Get current user's active contract."""
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    contract = profile_service.get_contract(current_user.odoo_employee_id)
    if not contract:
        raise HTTPException(status_code=404, detail="No active contract found")
    return contract
