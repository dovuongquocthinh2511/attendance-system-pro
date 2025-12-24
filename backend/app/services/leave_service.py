from datetime import date, datetime
from typing import List, Optional, Dict, Any
from app.services.odoo_client import odoo_client
from app.core.exceptions import OdooAPIError

class LeaveService:
    def create_request(self, employee_id: int, leave_type_id: int, date_from: date, date_to: date, description: str = "") -> int:
        """
        Create a new leave request in 'draft' state.
        """
        self._validate_dates(date_from, date_to)
        
        vals = {
            'employee_id': employee_id,
            'holiday_status_id': leave_type_id,
            'request_date_from': date_from.strftime('%Y-%m-%d'),
            'request_date_to': date_to.strftime('%Y-%m-%d'),
            'name': description,
            'state': 'draft'
        }
        
        try:
            leave_id = odoo_client.execute_kw('hr.leave', 'create', [vals])
            return leave_id
        except Exception as e:
            raise OdooAPIError(f"Failed to create leave request: {str(e)}")

    def confirm_request(self, leave_id: int, employee_id: int) -> bool:
        """
        Transition from 'draft' to 'confirm'.
        Performs validation: Overlap check and Balance check.
        """
        # 1. Get request details
        request = self._get_request(leave_id)
        if not request:
            raise ValueError("Leave request not found")
            
        if request['employee_id'][0] != employee_id:
             raise ValueError("Unauthorized to confirm this request")

        if request['state'] != 'draft':
            raise ValueError(f"Invalid state transition from {request['state']} to confirm")

        # 2. Check overlap
        date_from = datetime.strptime(request['request_date_from'], '%Y-%m-%d').date()
        date_to = datetime.strptime(request['request_date_to'], '%Y-%m-%d').date()
        
        if self._check_overlap(employee_id, date_from, date_to, exclude_id=leave_id):
             raise ValueError("Leave request overlaps with an existing approved or confirmed leave")

        # 3. Check balance (Simple check, Odoo often handles this, but we can double check)
        # For complexity, let's rely on Odoo's constraint for now or implement generic check if needed.
        # Requirement says "Check available allocation".
        if not self._check_balance(employee_id, request['holiday_status_id'][0], request['number_of_days']):
             raise ValueError("Insufficient leave balance")

        # 4. Transition
        try:
            # In Odoo 'action_confirm' is the method, or writing state 'confirm'. 
            # Usually calling the button method is safer as it triggers workflows.
            # But let's try writing state first or 'action_confirm'.
            # 'action_confirm' is standard for hr.leave.
            odoo_client.execute_kw('hr.leave', 'action_confirm', [[leave_id]])
            return True
        except Exception as e:
            raise OdooAPIError(f"Failed to confirm leave: {str(e)}")

    def approve_request(self, leave_id: int) -> bool:
        """Manager approves (validate)"""
        try:
            odoo_client.execute_kw('hr.leave', 'action_validate', [[leave_id]])
            return True
        except Exception as e:
            raise OdooAPIError(f"Failed to approve leave: {str(e)}")

    def reject_request(self, leave_id: int) -> bool:
        """Manager refuses (reject)"""
        try:
            odoo_client.execute_kw('hr.leave', 'action_refuse', [[leave_id]])
            return True
        except Exception as e:
            raise OdooAPIError(f"Failed to reject leave: {str(e)}")

    def get_history(self, employee_id: int, limit: int = 20) -> List[Dict]:
        domain = [['employee_id', '=', employee_id]]
        fields = ['id', 'holiday_status_id', 'request_date_from', 'request_date_to', 'number_of_days', 'state', 'name']
        return odoo_client.search_read('hr.leave', domain, fields, limit=limit, order='request_date_from desc')

    def get_balance(self, employee_id: int) -> List[Dict]:
        """
        Get leave balance (Allocation - Taken).
        Uses 'hr.leave.allocation' or 'hr.leave.type' virtual fields if available.
        Standard Odoo way: Get allocations and subtract leaves, or use 'get_employees_days' method on hr.leave.
        """
        # Using Odoo's helper method if possible is best. 'get_employees_days' returns dict of {type_id: {remaining...}}
        try:
            # We need to pass list of employee_ids
            allocations = odoo_client.execute_kw('hr.leave', 'get_employees_days', [[employee_id]])
            # Structure: {employee_id: {type_id: {remaining_leaves: x, ...}}}
            if not allocations or employee_id not in allocations:
                return []
            
            result = []
            user_data = allocations[employee_id]
            # Need to fetch type names to map type_id -> name
            type_ids = list(user_data.keys())
            types = odoo_client.search_read('hr.leave.type', [['id', 'in', type_ids]], ['id', 'name'])
            type_map = {t['id']: t['name'] for t in types}

            for type_id, data in user_data.items():
                if type_id in type_map:
                    result.append({
                        'type_id': type_id,
                        'name': type_map[type_id],
                        'remaining': data.get('remaining_leaves', 0),
                        'allocated': data.get('max_leaves', 0),
                        'taken': data.get('leaves_taken', 0)
                    })
            return result
        except Exception:
             # Fallback or empty if method shouldn't fail
             return []

    def _validate_dates(self, date_from: date, date_to: date):
        if date_to < date_from:
            raise ValueError("End date must be greater than or equal to start date")
        if date_from < date.today():
             # Requirement 3.5 says "dates not in past". 
             # Assuming this means creating a *new* request for the past is disallowed? 
             # Or just modifying? Let's assume STRICT for create.
             raise ValueError("Start date cannot be in the past")

    def _get_request(self, leave_id: int) -> Dict:
        records = odoo_client.search_read('hr.leave', [['id', '=', leave_id]], 
            ['id', 'state', 'employee_id', 'request_date_from', 'request_date_to', 'holiday_status_id', 'number_of_days'])
        return records[0] if records else None

    def _check_overlap(self, employee_id: int, date_from: date, date_to: date, exclude_id: int = None) -> bool:
        domain = [
            ['employee_id', '=', employee_id],
            ['state', 'in', ['confirm', 'validate', 'validate1']], # Overlap with active leaves
            ['request_date_from', '<=', date_to.strftime('%Y-%m-%d')],
            ['request_date_to', '>=', date_from.strftime('%Y-%m-%d')]
        ]
        if exclude_id:
            domain.append(['id', '!=', exclude_id])
            
        count = odoo_client.execute_kw('hr.leave', 'search_count', [domain])
        return count > 0

    def _check_balance(self, employee_id: int, type_id: int, days_needed: float) -> bool:
         # Use get_employees_days logic to check specific type
         try:
            allocations = odoo_client.execute_kw('hr.leave', 'get_employees_days', [[employee_id]])
            if not allocations or employee_id not in allocations:
                return False
            
            type_data = allocations[employee_id].get(type_id)
            if not type_data:
                # If no allocation found, implies 0 balance usually, unless type doesn't track balance?
                # Let's assume default 0.
                return False
                
            return type_data.get('remaining_leaves', 0) >= days_needed
         except:
             return False

leave_service = LeaveService()
