from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import date
from pydantic import BaseModel
from app.api import deps
from app.models.user import User
from app.services.leave_service import leave_service

router = APIRouter()

class LeaveRequestCreate(BaseModel):
    leave_type_id: int
    date_from: date
    date_to: date
    description: str = ""

@router.post("/request")
def create_request(
    request: LeaveRequestCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """Create a drafted leave request."""
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
    
    try:
        leave_id = leave_service.create_request(
            current_user.odoo_employee_id,
            request.leave_type_id,
            request.date_from,
            request.date_to,
            request.description
        )
        return {"msg": "Leave request created", "id": leave_id, "state": "draft"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{leave_id}/confirm")
def confirm_request(
    leave_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """Confirm a draft leave request."""
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    try:
        leave_service.confirm_request(leave_id, current_user.odoo_employee_id)
        return {"msg": "Leave request confirmed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history")
def get_history(
    current_user: User = Depends(deps.get_current_user)
):
    """Get leave history."""
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
    return leave_service.get_history(current_user.odoo_employee_id)

@router.get("/balance")
def get_balance(
    current_user: User = Depends(deps.get_current_user)
):
    """Get leave balances."""
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
    return leave_service.get_balance(current_user.odoo_employee_id)
    return leave_service.get_balance(current_user.odoo_employee_id)

@router.get("/types")
def get_leave_types(current_user: User = Depends(deps.get_current_user)):
    """Get available leave types."""
    return leave_service.get_leave_types()

@router.post("/{leave_id}/approve")
def approve_request(
    leave_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """Manager approve leave."""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    try:
        leave_service.approve_request(leave_id)
        return {"msg": "Leave approved"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{leave_id}/reject")
def reject_request(
    leave_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """Manager reject leave."""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    try:
        leave_service.reject_request(leave_id)
        return {"msg": "Leave rejected"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pending")
def get_pending_requests(
    current_user: User = Depends(deps.get_current_user)
):
    """Manager get pending requests."""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    return leave_service.get_pending_requests(current_user.odoo_employee_id)
