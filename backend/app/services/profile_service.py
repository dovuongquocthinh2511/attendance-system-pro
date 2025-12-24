from typing import Dict, Any, Optional
from app.services.odoo_client import odoo_client
from app.core.exceptions import OdooAPIError

class ProfileService:
    def get_profile(self, odoo_employee_id: int) -> Dict[str, Any]:
        """
        Fetch employee profile from Odoo.
        """
        fields = [
            'id', 'name', 'job_title', 'department_id', 'work_email', 'mobile_phone',
            'work_phone', 'work_location_id', 'parent_id', 'birthday', 'identification_id'
        ]
        records = odoo_client.search_read('hr.employee', [['id', '=', odoo_employee_id]], fields)
        return records[0] if records else {}

    def update_profile(self, odoo_employee_id: int, data: Dict[str, Any]) -> bool:
        """
        Update allowed profile fields in Odoo.
        """
        # Whitelist allowed fields to prevent overwriting sensitive data
        ALLOWED_FIELDS = {'mobile_phone', 'work_email', 'identification_id', 'birthday'}
        
        updates = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
        if not updates:
            return False # Nothing to update
            
        try:
            return odoo_client.execute_kw('hr.employee', 'write', [[odoo_employee_id], updates])
        except Exception as e:
            raise OdooAPIError(f"Failed to update profile: {str(e)}")

    def get_contract(self, odoo_employee_id: int) -> Dict[str, Any]:
        """
        Fetch active contract for the employee.
        """
        # Find contract where employee_id matches and state is open/close (or just active)
        domain = [
            ['employee_id', '=', odoo_employee_id],
            ['state', 'in', ['open', 'close', 'draft']] 
        ]
        # Sort by date_start desc to get latest
        fields = ['id', 'name', 'wage', 'state', 'date_start', 'date_end', 'job_id', 'department_id']
        records = odoo_client.search_read('hr.contract', domain, fields, order='date_start desc', limit=1)
        return records[0] if records else {}

profile_service = ProfileService()
