from typing import Optional
from pydantic import BaseModel

class AttendanceBase(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ip_address: Optional[str] = None
    mode: Optional[str] = "manual"

class CheckInRequest(AttendanceBase):
    pass

class CheckOutRequest(AttendanceBase):
    pass

class AttendanceStatusResponse(BaseModel):
    is_checked_in: bool
    check_in_time: Optional[str] = None
    record_id: Optional[int] = None

class AttendanceSummaryResponse(BaseModel):
    month: int
    year: int
    total_hours: float
    attendance_count: int
