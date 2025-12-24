from fastapi import HTTPException
from typing import Any, Optional, Dict

class BestmixException(Exception):
    """Base exception for Bestmix Pro"""
    def __init__(self, error_code: str, message: str, status_code: int = 400):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# --- Define Error Codes (Enum-like) ---
class ErrorCodes:
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    FORBIDDEN = "FORBIDDEN"
    ODOO_UNAVAILABLE = "ODOO_UNAVAILABLE"
    ODOO_ERROR = "ODOO_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DUPLICATE_CHECKIN = "DUPLICATE_CHECKIN"
    LEAVE_OVERLAP = "LEAVE_OVERLAP"
    USER_NOT_FOUND = "USER_NOT_FOUND" 
    NOT_FOUND = "NOT_FOUND"

# --- Custom Exceptions ---

class AuthenticationError(BestmixException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            error_code=ErrorCodes.INVALID_CREDENTIALS, 
            message=message, 
            status_code=401
        )

class AuthorizationError(BestmixException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            error_code=ErrorCodes.FORBIDDEN, 
            message=message, 
            status_code=403
        )

class OdooConnectionError(BestmixException):
    def __init__(self, message: str = "Cannot connect to Odoo"):
        super().__init__(
            error_code=ErrorCodes.ODOO_UNAVAILABLE, 
            message=message, 
            status_code=503
        )

class OdooAPIError(BestmixException):
    def __init__(self, message: str = "Odoo returned an error"):
        super().__init__(
            error_code=ErrorCodes.ODOO_ERROR, 
            message=message, 
            status_code=502
        )

class DuplicateCheckinError(BestmixException):
    def __init__(self, message: str = "Employee is already checked in"):
        super().__init__(
            error_code=ErrorCodes.DUPLICATE_CHECKIN, 
            message=message, 
            status_code=400
        )

class LeaveOverlapError(BestmixException):
    def __init__(self, message: str = "Leave request overlaps with existing leave"):
        super().__init__(
            error_code=ErrorCodes.LEAVE_OVERLAP, 
            message=message, 
            status_code=400
        )

class NotFoundError(BestmixException):
     def __init__(self, message: str = "Resource not found"):
        super().__init__(
            error_code=ErrorCodes.NOT_FOUND, 
            message=message, 
            status_code=404
        )
