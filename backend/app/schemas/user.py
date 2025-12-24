from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    role: Optional[str] = "employee"
    odoo_employee_id: Optional[int] = None
    is_active: Optional[bool] = True

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    odoo_employee_id: Optional[int] = None
    is_active: Optional[bool] = None

# Properties to return via API
class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Login schema
class UserLogin(BaseModel):
    username: str
    password: str