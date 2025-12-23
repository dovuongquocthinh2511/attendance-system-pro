class OdooBaseException(Exception):
    """Base exception for Odoo errors"""
    pass

class OdooConnectionError(OdooBaseException):
    """Failed to connect to Odoo server"""
    pass

class OdooAuthError(OdooBaseException):
    """Authentication failed"""
    pass

class OdooAPIError(OdooBaseException):
    """Error returned by Odoo API execution"""
    pass
