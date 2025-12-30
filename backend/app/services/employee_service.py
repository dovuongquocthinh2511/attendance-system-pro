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

    def find_by_email_or_phone(self, email: str = None, phone: str = None) -> Optional[int]:
        """
        Find Odoo employee by Email OR Phone (Mobile/Work).
        """
        if not email and not phone:
            return None
            
        domain = []
        # Match Work Email
        if email:
            domain.append(['work_email', '=', email])
            
        # Match Mobile or Work Phone
        if phone:
            domain.append(['mobile_phone', '=', phone])
            domain.append(['work_phone', '=', phone])
            
        if not domain:
            return None
            
        # Prefix notation for ORs: ['|', '|', A, B, C]
        final_domain = []
        if len(domain) > 1:
            final_domain = ['|'] * (len(domain) - 1)
        final_domain.extend(domain)
        
        try:
            employees = odoo_client.search_read('hr.employee', final_domain, ['id'], limit=1)
            return employees[0]['id'] if employees else None
        except Exception as e:
            print(f"Error searching Odoo employee: {e}")
            return None

employee_service = EmployeeService()
