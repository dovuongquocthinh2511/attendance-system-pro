from datetime import date
from pydantic import BaseModel

class LeaveRequestCreate(BaseModel):
    leave_type_id: int
    date_from: date
    date_to: date
    description: str = ""
