from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base
from datetime import datetime
from sqlalchemy import DateTime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=True) # Login bằng SĐT
    password_hash = Column(String, nullable=False) # Lưu hash, không lưu plain text
    role = Column(String, default="employee") # 'employee', 'manager', 'admin'
    odoo_employee_id = Column(Integer, nullable=True) # Link sang Odoo
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)    