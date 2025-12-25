from datetime import datetime
from typing import List, Optional, Any
from app.services.odoo_client import odoo_client
from app.core.exceptions import OdooAPIError, DuplicateCheckinError, NotFoundError

class AttendanceService:
    def get_status(self, odoo_employee_id: int) -> Optional[dict]:
        """
        Check if employee is currently checked in.
        Returns the open attendance record if exists, else None.
        """
        domain = [
            ['employee_id', '=', odoo_employee_id],
            ['check_out', '=', False]
        ]
        # Sort by check_in desc to get latest
        records = odoo_client.search_read('hr.attendance', domain, ['id', 'check_in'], limit=1)
        return records[0] if records else None

    def check_in(
        self, 
        odoo_employee_id: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        ip_address: Optional[str] = None,
        mode: Optional[str] = "manual"
    ) -> int:
        """
        Create a new attendance record (Check In).
        Prevents duplicate check-in if already checked in.
        Includes metadata: GPS, IP, Mode.
        """
        # 1. Validation: Check if already checked in
        current_status = self.get_status(odoo_employee_id)
        if current_status:
            raise DuplicateCheckinError()

        vals = {
            'employee_id': odoo_employee_id,
            'in_latitude': latitude,
            'in_longitude': longitude,
            'in_ip_address': ip_address,
            'in_mode': mode
        }

        try:
            attendance_id = odoo_client.execute_kw(
                'hr.attendance', 'create', [vals]
            )
            return attendance_id
        except Exception as e:
            raise OdooAPIError(f"Failed to check in: {str(e)}")

    def check_out(
        self, 
        odoo_employee_id: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        ip_address: Optional[str] = None,
        mode: Optional[str] = "manual"
    ) -> bool:
        """
        Update the open attendance record (Check Out).
        Includes metadata: GPS, IP, Mode.
        """
        # 1. specific logic: Find open attendance
        current_status = self.get_status(odoo_employee_id)
        if not current_status:
            raise NotFoundError("Employee is not checked in")

        attendance_id = current_status['id']
        
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        vals = {
            'check_out': now,
            'out_latitude': latitude,
            'out_longitude': longitude,
            'out_ip_address': ip_address,
            'out_mode': mode
        }

        try:
            success = odoo_client.execute_kw(
                'hr.attendance', 'write', [[attendance_id], vals]
            )
            return success
        except Exception as e:
            raise OdooAPIError(f"Failed to check out: {str(e)}")

    def get_history(self, odoo_employee_id: int, limit: int = 30) -> List[dict]:
        """
        Get attendance history for employee.
        """
        domain = [['employee_id', '=', odoo_employee_id]]
        fields = ['id', 'employee_id', 'check_in', 'check_out', 'worked_hours']
        
        return odoo_client.execute_kw(
            'hr.attendance', 'search_read', [domain], 
            {'fields': fields, 'limit': limit, 'order': 'check_in desc'}
        )

    def get_summary(self, odoo_employee_id: int, month: int, year: int) -> dict:
        """
        Get monthly attendance summary (total worked hours).
        """
        # 1. Determine date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
            
        # 2. Search records within range
        domain = [
            ['employee_id', '=', odoo_employee_id],
            ['check_in', '>=', start_date.strftime('%Y-%m-%d')],
            ['check_in', '<', end_date.strftime('%Y-%m-%d')]
        ]
        
        records = odoo_client.execute_kw(
            'hr.attendance', 'search_read', [domain], 
            {'fields': ['worked_hours']}
        )
        
        # 3. Sum worked_hours
        total_hours = sum(r.get('worked_hours', 0.0) for r in records)
        
        return {
            "month": month,
            "year": year,
            "total_hours": round(total_hours, 2),
            "attendance_count": len(records)
        }

attendance_service = AttendanceService()
