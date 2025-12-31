import xmlrpc.client
from typing import Any, List, Optional
from app.core.logger import logger
from app.core.config import settings
from app.core.exceptions import OdooConnectionError, OdooAPIError, AuthenticationError

# Alias for backward compatibility if needed, or just use AuthenticationError
OdooAuthError = AuthenticationError

class OdooClient:
    def __init__(self):
        self.url = settings.ODOO_URL
        self.db = settings.ODOO_DB
        self.username = settings.ODOO_USERNAME
        self.password = settings.ODOO_PASSWORD
        self.uid: Optional[int] = None
        self.common = None
        self.models = None

    def connect(self):
        """Establish connection to Odoo and authenticate."""
        if self.uid:
            return  # Already connected and authenticated

        logger.info(f"Connecting to Odoo: URL={self.url}, DB={self.db}, User={self.username}")

        if not self.db:
             raise OdooConnectionError("Odoo Database name (ODOO_DB) is not configured.")

        try:
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            
            if not self.uid:
                raise AuthenticationError(f"Authentication failed for user {self.username}")
                
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            logger.info(f"--- Connected to Odoo successfully! UID: {self.uid} ---")
            
        except ConnectionRefusedError:
             raise OdooConnectionError(f"Could not connect to Odoo at {self.url}")
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise e
            raise OdooConnectionError(f"Odoo connection error: {str(e)}")

    def execute_kw(self, model: str, method: str, args: List[Any], kwargs: dict = None) -> Any:
        """Execute a method on an Odoo model."""
        if not self.uid:
            self.connect()

        if kwargs is None:
            kwargs = {}

        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )
        except xmlrpc.client.Fault as e:
            raise OdooAPIError(f"Odoo Fault: {e.faultString} (Code: {e.faultCode})")
        except Exception as e:
             raise OdooAPIError(f"Odoo Execution Error: {str(e)}")

    def search_read(self, model: str, domain: List[Any], fields: List[str], limit: int = None, order: str = None) -> List[dict]:
        """Helper for search_read method."""
        kwargs = {'fields': fields}
        if limit:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order
        return self.execute_kw(model, 'search_read', [domain], kwargs)

odoo_client = OdooClient()
