from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime

class OdooEmployee(BaseModel):
    id: int
    name: str
    job_title: Optional[str] = None
    department_id: Optional[List[Union[int, str]]] = None # Odoo returns [id, "Name"] usually
    work_email: Optional[str] = None
    mobile_phone: Optional[str] = None

class OdooAttendance(BaseModel):
    id: int
    employee_id: List[Union[int, str]]
    check_in: datetime = Field(..., description="UTC Check-in time")
    check_out: Optional[datetime] = Field(None, description="UTC Check-out time")

