from pydantic import BaseModel
from typing import Optional
from datetime import date

class ProfileUpdateRequest(BaseModel):
    mobile_phone: Optional[str] = None
    work_email: Optional[str] = None
    identification_id: Optional[str] = None
    birthday: Optional[date] = None
