from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any
from app.api import deps
from app.models.user import User
from app.services.profile_service import profile_service
from app.schemas.response import APIResponse
from app.schemas.odoo import OdooEmployee, OdooContract
from app.schemas.profile import ProfileUpdateRequest
from app.schemas.common import ActionResponse

router = APIRouter()

@router.get("/", response_model=APIResponse[OdooEmployee])
def get_my_profile(current_user: User = Depends(deps.get_current_user)):
    """Get current user's Odoo profile."""
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    profile = profile_service.get_profile(current_user.odoo_employee_id)
    return APIResponse(data=profile)

@router.put("/", response_model=APIResponse[ActionResponse])
def update_my_profile(
    updates: ProfileUpdateRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update current user's profile.
    Allowed keys: mobile_phone, work_email, identification_id, birthday.
    """
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    try:
        # Convert pydantic model to dict, excluding unset fields
        update_data = updates.dict(exclude_unset=True)
        
        success = profile_service.update_profile(current_user.odoo_employee_id, update_data)
        if success:
             return APIResponse(data=ActionResponse(msg="Profile updated successfully", id=current_user.odoo_employee_id, state="updated"))
        return APIResponse(data=ActionResponse(msg="No changes made or invalid fields", id=current_user.odoo_employee_id, state="no_change"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/contract", response_model=APIResponse[OdooContract])
def get_my_contract(current_user: User = Depends(deps.get_current_user)):
    """Get current user's active contract."""
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    contract = profile_service.get_contract(current_user.odoo_employee_id)
    if not contract:
        raise HTTPException(status_code=404, detail="No active contract found")
    return APIResponse(data=contract)
