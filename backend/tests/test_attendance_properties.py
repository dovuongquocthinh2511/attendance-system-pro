from hypothesis import given, strategies as st
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from app.services.attendance_service import attendance_service
from app.core.exceptions import DuplicateCheckinError, NotFoundError

# --- Property 5: Duplicate Check-in Prevention ---
# Validates Requirement 2.6
@given(odoo_id=st.integers(min_value=1))
def test_duplicate_checkin_prevention(odoo_id):
    # Mock get_status to return a record (simulating already checked in)
    with patch('app.services.attendance_service.attendance_service.get_status') as mock_status:
        mock_status.return_value = {'id': 123, 'check_in': '2023-01-01 08:00:00'}
        
        # Expect DuplicateCheckinError when trying to check in again
        try:
            attendance_service.check_in(odoo_id)
            assert False, "Should have raised DuplicateCheckinError"
        except DuplicateCheckinError as e:
            assert str(e) == "Employee is already checked in"

# --- Property 3: Record Consistency ---
# Validates Requirement 2.1, 2.2
# Validates that check-out is only allowed if checked in
@given(odoo_id=st.integers(min_value=1))
def test_checkout_consistency(odoo_id):
    with patch('app.services.attendance_service.attendance_service.get_status') as mock_status:
        # Case 1: NOT checked in -> Check-out fails
        mock_status.return_value = None
        try:
            attendance_service.check_out(odoo_id)
            assert False, "Should have raised NotFoundError if not checked in"
        except NotFoundError as e:
            assert str(e) == "Employee is not checked in"

        # Case 2: Checked in -> Check-out succeeds
        mock_status.return_value = {'id': 123}
        with patch('app.services.attendance_service.odoo_client.execute_kw') as mock_odoo:
            mock_odoo.return_value = True
            assert attendance_service.check_out(odoo_id) is True

# --- Property 4: History Ordering ---
# Validates Requirement 2.3
# We verify that if we ask for history, the service passes 'order': 'check_in desc' to Odoo
@given(odoo_id=st.integers(min_value=1), limit=st.integers(min_value=1, max_value=100))
def test_history_ordering_param(odoo_id, limit):
    with patch('app.services.attendance_service.odoo_client.execute_kw') as mock_odoo:
        mock_odoo.return_value = [] # Return empty list just to allow call to finish
        
        attendance_service.get_history(odoo_id, limit=limit)
        
        # Verify call args
        args, kwargs = mock_odoo.call_args
        # args[0] is model, args[1] is method
        assert args[0] == 'hr.attendance'
        assert args[1] == 'search_read'
        
        # Check if 'order' param is present in kwargs or args[3]
        # Our service passes it in the 4th arg (kwargs equivalent in execute_kw wrapper logic)
        # execute_kw(self, model, method, args, kwargs)
        # search_read params in service: [domain], {'fields':..., 'order':...}
        
        passed_kwargs = args[3]
        assert 'order' in passed_kwargs
        assert passed_kwargs['order'] == 'check_in desc'
        assert passed_kwargs['limit'] == limit

# --- Property 6: Summary Accuracy ---
# Validates Requirement 2.7
@given(
    odoo_id=st.integers(min_value=1),
    hours_list=st.lists(st.floats(min_value=0.0, max_value=24.0), min_size=1, max_size=10)
)
def test_summary_accuracy(odoo_id, hours_list):
    # Setup: Mock records with specific 'worked_hours'
    mock_records = [{'worked_hours': h} for h in hours_list]
    expected_total = round(sum(hours_list), 2)
    
    with patch('app.services.attendance_service.odoo_client.execute_kw') as mock_odoo:
        mock_odoo.return_value = mock_records
        
        # Action: Get summary
        summary = attendance_service.get_summary(odoo_id, month=1, year=2024)
        
        # Assert
        # Use simple float comparison with small tolerance or exact if rounded
        assert abs(summary['total_hours'] - expected_total) < 0.01
        assert summary['attendance_count'] == len(hours_list)
