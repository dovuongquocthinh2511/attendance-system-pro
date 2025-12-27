from datetime import date, datetime
from typing import List, Optional, Dict, Any
from app.services.odoo_client import odoo_client
from app.core.exceptions import OdooAPIError, LeaveOverlapError, AuthorizationError, NotFoundError

class LeaveService:
    def create_request(self, employee_id: int, leave_type_id: int, date_from: date, date_to: date, description: str = "") -> int:
        """Create a new leave request in 'draft' state."""
        self._validate_dates(date_from, date_to)
        
        vals = {
            'employee_id': employee_id,
            'holiday_status_id': leave_type_id,
            'request_date_from': date_from.strftime('%Y-%m-%d'),
            'request_date_to': date_to.strftime('%Y-%m-%d'),
            'name': description
        }
        
        try:
            leave_id = odoo_client.execute_kw('hr.leave', 'create', [vals])
            return leave_id
        except Exception as e:
            raise OdooAPIError(f"Failed to create leave request: {str(e)}")

    def confirm_request(self, leave_id: int, employee_id: int) -> str:
        """Transition from 'draft' to 'confirm'. Validation: Overlap & Balance."""
        request = self._get_request(leave_id)
        if not request:
            raise NotFoundError("Leave request not found")
            
        if request['employee_id'][0] != employee_id:
             raise AuthorizationError("Unauthorized to confirm this request")

        if request['state'] == 'confirm':
            return 'confirm'

        if request['state'] != 'draft':
            raise OdooAPIError(f"Invalid state transition from {request['state']} to confirm")

        date_from = datetime.strptime(request['request_date_from'], '%Y-%m-%d').date()
        date_to = datetime.strptime(request['request_date_to'], '%Y-%m-%d').date()
        
        if self._check_overlap(employee_id, date_from, date_to, exclude_id=leave_id):
             raise LeaveOverlapError()

        if not self._check_balance(employee_id, request['holiday_status_id'][0], request['number_of_days']):
             raise OdooAPIError("Insufficient leave balance")

        try:
            odoo_client.execute_kw('hr.leave', 'action_confirm', [[leave_id]])
            return 'confirm'
        except Exception as e:
            raise OdooAPIError(f"Failed to confirm leave: {str(e)}")

    def approve_request(self, leave_id: int) -> str:
        """Manager approves (validate)"""
        try:
            odoo_client.execute_kw('hr.leave', 'action_validate', [[leave_id]])
            return 'validate'
        except Exception as e:
            raise OdooAPIError(f"Failed to approve leave: {str(e)}")

    def reject_request(self, leave_id: int) -> str:
        """Manager refuses (reject)"""
        try:
            odoo_client.execute_kw('hr.leave', 'action_refuse', [[leave_id]])
            return 'refuse'
        except Exception as e:
            raise OdooAPIError(f"Failed to reject leave: {str(e)}")

    def get_history(self, employee_id: int, limit: int = 20) -> List[Dict]:
        domain = [['employee_id', '=', employee_id]]
        fields = ['id', 'holiday_status_id', 'request_date_from', 'request_date_to', 'number_of_days', 'state', 'name', 'employee_id']
        return odoo_client.search_read('hr.leave', domain, fields, limit=limit, order='request_date_from desc')

    def get_balance(self, employee_id: int) -> List[Dict]:
        """
        Get leave balance (Allocation - Taken).
        Manual calculation as 'get_employees_days' is unavailable in some Odoo versions.
        """
        try:
            # 1. Get Granted Allocations
            allocations = odoo_client.search_read(
                'hr.leave.allocation', 
                [['employee_id', '=', employee_id], ['state', '=', 'validate']], 
                ['holiday_status_id', 'number_of_days']
            )
            
            # 2. Get Taken Leaves (Confirmed or Validated)
            leaves = odoo_client.search_read(
                'hr.leave', 
                [['employee_id', '=', employee_id], ['state', 'in', ['confirm', 'validate', 'validate1']]], 
                ['holiday_status_id', 'number_of_days']
            )

            # 3. Aggregate Data
            balance_map = {}

            # Process Allocations
            for alloc in allocations:
                if not alloc['holiday_status_id']: continue
                type_id = alloc['holiday_status_id'][0] # [id, name]
                type_name = alloc['holiday_status_id'][1]
                
                if type_id not in balance_map:
                    balance_map[type_id] = {'type_id': type_id, 'name': type_name, 'allocated': 0.0, 'taken': 0.0}
                
                balance_map[type_id]['allocated'] += alloc['number_of_days']

            # Process Leaves
            for leave in leaves:
                if not leave['holiday_status_id']: continue
                type_id = leave['holiday_status_id'][0]
                # If no allocation exists for this type (e.g. Unpaid), fetch name from leave or ignore?
                # Usually standard leaves require allocation OR are unlimited.
                # If not in map, we add it.
                if type_id not in balance_map:
                    type_name = leave['holiday_status_id'][1]
                    balance_map[type_id] = {'type_id': type_id, 'name': type_name, 'allocated': 0.0, 'taken': 0.0}
                
                balance_map[type_id]['taken'] += leave['number_of_days']

            # 4. Format Result
            result = []
            for type_id, data in balance_map.items():
                result.append({
                    'type_id': type_id,
                    'name': data['name'],
                    'remaining': data['allocated'] - data['taken'],
                    'allocated': data['allocated'],
                    'taken': data['taken']
                })
                
            return result

        except Exception as e:
            # Log specific error if needed, but for API safety we return empty list or re-raise if critical
            print(f"Error calculating balance: {e}") # Simple logging
            return []

    def get_leave_types(self) -> List[Dict]:
        """Get all leave types."""
        return odoo_client.search_read('hr.leave.type', [], ['id', 'name', 'allocation_validation_type'])

    def get_pending_requests(self, manager_employee_id: int) -> List[Dict]:
        """
        Get pending requests for a manager.
        """
        domain = [['state', '=', 'confirm']]
        
        # Simple Manager Scope: If manager has department, filter by that department?
        # Ideally we fetch department_id if needed, but for now we follow basic requirement.
        # To be robust, let's keep it simple for now or fetch if required.
        
        fields = ['id', 'employee_id', 'holiday_status_id', 'request_date_from', 'request_date_to', 'number_of_days', 'name', 'state']
        return odoo_client.search_read('hr.leave', domain, fields, order='request_date_from asc')

    def _validate_dates(self, date_from: date, date_to: date):
        if date_to < date_from:
            raise OdooAPIError("End date must be greater than or equal to start date")
        if date_from < date.today():
             raise OdooAPIError("Start date cannot be in the past")

    def _get_request(self, leave_id: int) -> Dict:
        records = odoo_client.search_read('hr.leave', [['id', '=', leave_id]], 
            ['id', 'state', 'employee_id', 'request_date_from', 'request_date_to', 'holiday_status_id', 'number_of_days'])
        return records[0] if records else None

    def _check_overlap(self, employee_id: int, date_from: date, date_to: date, exclude_id: int = None) -> bool:
        domain = [
            ['employee_id', '=', employee_id],
            ['state', 'in', ['confirm', 'validate', 'validate1']], 
            ['request_date_from', '<=', date_to.strftime('%Y-%m-%d')],
            ['request_date_to', '>=', date_from.strftime('%Y-%m-%d')]
        ]
        if exclude_id:
            domain.append(['id', '!=', exclude_id])
            
        count = odoo_client.execute_kw('hr.leave', 'search_count', [domain])
        return count > 0

    def _check_balance(self, employee_id: int, type_id: int, days_needed: float) -> bool:
         try:
            allocations = odoo_client.execute_kw('hr.leave', 'get_employees_days', [[employee_id]])
            if not allocations or employee_id not in allocations:
                return False
            type_data = allocations[employee_id].get(type_id)
            return type_data and type_data.get('remaining_leaves', 0) >= days_needed
         except:
             return False

leave_service = LeaveService()
