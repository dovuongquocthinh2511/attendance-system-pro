from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api import deps
from app.models.user import User
from app.services.attendance_service import attendance_service
from app.services.employee_service import employee_service
from app.schemas.odoo import OdooAttendance
from app.schemas.attendance import CheckInRequest, CheckOutRequest, AttendanceStatusResponse, AttendanceSummaryResponse
from app.schemas.response import APIResponse
from app.schemas.common import ActionResponse

router = APIRouter()

@router.get("/status", response_model=APIResponse[AttendanceStatusResponse])
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
        return APIResponse(data=AttendanceStatusResponse(
            is_checked_in=True,
            check_in_time=str(record['check_in']),
            record_id=record['id']
        ))
    return APIResponse(data=AttendanceStatusResponse(is_checked_in=False))

@router.post("/check-in", response_model=APIResponse[ActionResponse])
def check_in(
    data: CheckInRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Check in the current user.
    Input: CheckInRequest (GPS, IP)
    """
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    try:
        attendance_id = attendance_service.check_in(
            odoo_employee_id=current_user.odoo_employee_id,
            latitude=data.latitude,
            longitude=data.longitude,
            ip_address=data.ip_address,
            mode=data.mode
        )
        return APIResponse(data=ActionResponse(msg="Checked in successfully", id=attendance_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-out", response_model=APIResponse[ActionResponse])
def check_out(
    data: CheckOutRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Check out the current user.
    Input: CheckOutRequest (GPS, IP)
    """
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")
        
    try:
        attendance_service.check_out(
            odoo_employee_id=current_user.odoo_employee_id,
            latitude=data.latitude,
            longitude=data.longitude,
            ip_address=data.ip_address,
            mode=data.mode
        )
        return APIResponse(data=ActionResponse(msg="Checked out successfully"))
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

@router.get("/summary", response_model=APIResponse[AttendanceSummaryResponse])
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
    # The service returns a dict, so we cast it to the model. 
    # Validating data before returning is safer.
    return APIResponse(data=AttendanceSummaryResponse(**summary))
