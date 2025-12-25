from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api import deps
from app.models.user import User
from app.services.attendance_service import attendance_service
from app.services.employee_service import employee_service
from app.schemas.odoo import OdooAttendance
from app.schemas.response import APIResponse

router = APIRouter()

@router.get("/status", response_model=APIResponse[dict])
def get_status(current_user: User = Depends(deps.get_current_user)):
    """
    Get current attendance status (checked in or not).
    """
    if not current_user.odoo_employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not linked to an Odoo employee"
        )
        
    record = attendance_service.get_status(current_user.odoo_employee_id)
    if record:
        return APIResponse(data={
            "is_checked_in": True,
            "check_in_time": record['check_in'],
            "record_id": record['id']
        })
    return APIResponse(data={"is_checked_in": False})

@router.post("/check-in", response_model=APIResponse[dict])
def check_in(current_user: User = Depends(deps.get_current_user)):
    """
    Check in the current user.
    """
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    try:
        attendance_id = attendance_service.check_in(current_user.odoo_employee_id)
        return APIResponse(data={"msg": "Checked in successfully", "id": attendance_id})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-out", response_model=APIResponse[dict])
def check_out(current_user: User = Depends(deps.get_current_user)):
    """
    Check out the current user.
    """
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    try:
        attendance_service.check_out(current_user.odoo_employee_id)
        return APIResponse(data={"msg": "Checked out successfully"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=APIResponse[List[OdooAttendance]])
def get_history(limit: int = 10, current_user: User = Depends(deps.get_current_user)):
    """
    Get attendance history.
    """
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    history = attendance_service.get_history(current_user.odoo_employee_id, limit=limit)
    return APIResponse(data=history)

@router.get("/summary", response_model=APIResponse[dict])
def get_summary(
    month: int, 
    year: int, 
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get monthly attendance summary.
    """
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    summary = attendance_service.get_summary(current_user.odoo_employee_id, month, year)
    return APIResponse(data=summary)
