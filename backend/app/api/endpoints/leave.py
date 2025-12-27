from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api import deps
from app.models.user import User
from app.services.leave_service import leave_service
from app.schemas.response import APIResponse
from app.schemas.odoo import OdooLeave, OdooLeaveType
from app.schemas.leave import LeaveCreateRequest, LeaveBalanceResponse
from app.schemas.common import ActionResponse

router = APIRouter()

@router.post("/request", response_model=APIResponse[ActionResponse])
def create_request(
    request: LeaveCreateRequest,
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
        return APIResponse(data=ActionResponse(msg="Leave request created", id=leave_id, state="draft"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{leave_id}/confirm", response_model=APIResponse[ActionResponse])
def confirm_request(
    leave_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """Confirm a draft leave request."""
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    try:
        new_state = leave_service.confirm_request(leave_id, current_user.odoo_employee_id)
        return APIResponse(data=ActionResponse(msg="Leave request confirmed", id=leave_id, state=new_state))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history", response_model=APIResponse[List[OdooLeave]])
def get_history(
    current_user: User = Depends(deps.get_current_user)
):
    """Get leave history."""
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
    history = leave_service.get_history(current_user.odoo_employee_id)
    return APIResponse(data=history)

@router.get("/balance", response_model=APIResponse[List[LeaveBalanceResponse]])
def get_balance(
    current_user: User = Depends(deps.get_current_user)
):
    """Get leave balances."""
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
    balance = leave_service.get_balance(current_user.odoo_employee_id)
    return APIResponse(data=balance)

@router.get("/types", response_model=APIResponse[List[OdooLeaveType]])
def get_leave_types(current_user: User = Depends(deps.get_current_user)):
    """Get available leave types."""
    types = leave_service.get_leave_types()
    return APIResponse(data=types)

@router.post("/{leave_id}/approve", response_model=APIResponse[ActionResponse])
def approve_request(
    leave_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """Manager approve leave."""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    try:
        new_state = leave_service.approve_request(leave_id)
        return APIResponse(data=ActionResponse(msg="Leave approved", id=leave_id, state=new_state))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{leave_id}/reject", response_model=APIResponse[ActionResponse])
def reject_request(
    leave_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """Manager reject leave."""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    try:
        new_state = leave_service.reject_request(leave_id)
        return APIResponse(data=ActionResponse(msg="Leave rejected", id=leave_id, state=new_state))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pending", response_model=APIResponse[List[OdooLeave]])
def get_pending_requests(
    current_user: User = Depends(deps.get_current_user)
):
    """Manager get pending requests."""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    pending = leave_service.get_pending_requests(current_user.odoo_employee_id)
    return APIResponse(data=pending)
