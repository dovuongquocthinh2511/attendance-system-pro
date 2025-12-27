from datetime import date
from pydantic import BaseModel

class LeaveCreateRequest(BaseModel):
    leave_type_id: int
    date_from: date
    date_to: date
    description: str = ""

class LeaveBalanceResponse(BaseModel):
    type_id: int
    name: str
    remaining: float
    allocated: float
    taken: float
