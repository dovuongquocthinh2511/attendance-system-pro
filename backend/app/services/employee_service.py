from typing import Optional
from app.services.odoo_client import odoo_client

class EmployeeService:
    def validate_odoo_employee_id(self, odoo_employee_id: int) -> bool:
        """
        Check if an employee ID exists in Odoo.
        Returns True if exists, False otherwise.
        """
        if not odoo_employee_id:
            return False
            
        try:
            # Search for employee with this ID
            # We don't need to read fields, just count/search
            count = odoo_client.execute_kw(
                'hr.employee', 
                'search_count', 
                [[['id', '=', odoo_employee_id]]]
            )
            return count > 0
        except Exception as e:
            # If connection fails or other error, we assume validation failed (safety)
            # Or we could log it. For now, return False.
            print(f"Error validating Odoo Employee ID: {e}")
            return False

employee_service = EmployeeService()
