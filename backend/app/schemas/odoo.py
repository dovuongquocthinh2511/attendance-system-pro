from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Union, Any
from datetime import datetime, date

# Generic Odoo Many2one field type: [id, "Name"] or False/None
OdooM2O = Optional[List[Union[int, str]]]

class OdooEmployee(BaseModel):
    id: int
    name: str
    job_title: Optional[str] = None
    department_id: OdooM2O = None
    work_email: Optional[str] = None
    mobile_phone: Optional[str] = None
    work_phone: Optional[str] = None
    work_location_id: OdooM2O = None
    parent_id: OdooM2O = None
    birthday: Optional[date] = None
    identification_id: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def parse_odoo_false(cls, data: Any) -> Any:
        """Convert Odoo's False values to None for all fields."""
        if isinstance(data, dict):
            return {
                k: (None if v is False else v) 
                for k, v in data.items()
            }
        return data

class OdooAttendance(BaseModel):
    id: int
    employee_id: List[Union[int, str]]
    check_in: datetime = Field(..., description="UTC Check-in time")
    check_out: Optional[datetime] = Field(None, description="UTC Check-out time")
    worked_hours: Optional[float] = 0.0

class OdooLeave(BaseModel):
    id: int
    employee_id: OdooM2O
    holiday_status_id: OdooM2O
    request_date_from: date
    request_date_to: date
    state: str
    number_of_days: float
    name: Optional[str] = ""

class OdooLeaveType(BaseModel):
    id: int
    name: str
    allocation_validation_type: Optional[str] = None

class OdooLeaveAllocation(BaseModel):
    id: int
    employee_id: OdooM2O
    holiday_status_id: OdooM2O
    number_of_days: float
    leaves_taken: float
    remaining_leaves: float

class OdooContract(BaseModel):
    id: int
    employee_id: OdooM2O
    name: str
    wage: float
    state: str
    date_start: date
    date_end: Optional[date] = None
    job_id: OdooM2O = None
    department_id: OdooM2O = None

    @model_validator(mode='before')
    @classmethod
    def parse_odoo_false(cls, data: Any) -> Any:
        # Re-use validator logic or import a base class. 
        # For simplicity, duplicate concise logic here to keep modules independent if no base class exists yet.
        if isinstance(data, dict):
            return {
                k: (None if v is False else v) 
                for k, v in data.items()
            }
        return data
