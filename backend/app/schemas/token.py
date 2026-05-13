from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    odoo_employee_id: Optional[int] = None

# Schema dùng để hứng dữ liệu sau khi giải mã Token
class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    odoo_employee_id: Optional[int] = None
    exp: Optional[int] = None