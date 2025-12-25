from typing import Optional
from pydantic import BaseModel

class AttendanceBase(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ip_address: Optional[str] = None
    mode: Optional[str] = "manual"

class AttendanceCheckIn(AttendanceBase):
    pass

class AttendanceCheckOut(AttendanceBase):
    pass

class AttendanceStatus(BaseModel):
    is_checked_in: bool
    check_in_time: Optional[str] = None
    record_id: Optional[int] = None

class AttendanceSummary(BaseModel):
    month: int
    year: int
    total_hours: float
    attendance_count: int
