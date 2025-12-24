from hypothesis import given, strategies as st
from unittest.mock import MagicMock, patch
from datetime import date, timedelta, datetime
from app.services.leave_service import leave_service

# --- Property 9: Leave Date Validation ---
# Requirement 3.5: End date >= Start date, Not in past
@given(
    start_offset=st.integers(min_value=-10, max_value=10),
    duration=st.integers(min_value=-10, max_value=10)
)
def test_leave_date_validation(start_offset, duration):
    today = date.today()
    start_date = today + timedelta(days=start_offset)
    end_date = start_date + timedelta(days=duration)
    
    # Logic to define expectation
    is_past = start_date < today
    is_invalid_range = end_date < start_date
    should_fail = is_past or is_invalid_range
    
    try:
        # We test the internal validation method directly for precise property testing
        leave_service._validate_dates(start_date, end_date)
        if should_fail:
            assert False, f"Should have failed for start={start_date}, end={end_date}"
    except ValueError as e:
        if not should_fail:
            assert False, f"Should NOT have failed: {str(e)}"

# --- Property 10: Overlap Detection ---
# Requirement 3.7
@given(
    existing_start=st.dates(min_value=date(2024, 1, 1), max_value=date(2024, 1, 10)),
    existing_duration=st.integers(min_value=1, max_value=5),
    new_start_offset=st.integers(min_value=-5, max_value=10),
    new_duration=st.integers(min_value=1, max_value=5)
)
def test_overlap_detection(existing_start, existing_duration, new_start_offset, new_duration):
    # Setup Existing Leave
    existing_end = existing_start + timedelta(days=existing_duration)
    
    # Setup New Request
    new_start = existing_start + timedelta(days=new_start_offset)
    new_end = new_start + timedelta(days=new_duration)
    
    # Determine basic overlap logic
    # Overlap if (StartA <= EndB) and (EndA >= StartB)
    overlap = (existing_start <= new_end) and (existing_end >= new_start)
    
    # Mock search_count to simulate existence check
    # We mock _check_overlap's odoo call. 
    # But wait, existing_start/end are inputs to the Property. 
    # We must mock the Odoo response to match "overlap expectation".
    # Actually, the Service logic asks Odoo for count based on domain.
    # To test the SERVICE logic ensuring it constructs domain correctly:
    
    with patch('app.services.leave_service.odoo_client.execute_kw') as mock_execute:
        # If we want to simulate Odoo finding an overlap, we allow search_count to return 1 if logic dictates?
        # No, simpler: We trust Odoo's search logic, but we want to verify our Service *checks* it.
        # But for Property Testing the business logic "Reject if overlap", 
        # let's mock the return of `_check_overlap` internal or `execute_kw`.
        
        # Let's test the helper _check_overlap directly? 
        # It relies on Odoo search query. 
        # Let's instead test confirm_request mocks.
        
        with patch('app.services.leave_service.leave_service._check_overlap') as mock_check:
            mock_check.return_value = overlap
            
            # Mock get_request to return valid draft
            with patch('app.services.leave_service.leave_service._get_request') as mock_get:
                mock_get.return_value = {
                    'employee_id': [1, 'Test'], 
                    'state': 'draft',
                    'request_date_from': new_start.strftime('%Y-%m-%d'),
                    'request_date_to': new_end.strftime('%Y-%m-%d'),
                    'holiday_status_id': [1, 'Time Off'],
                    'number_of_days': 1
                }
                
                # Mock balance check to pass
                with patch('app.services.leave_service.leave_service._check_balance', return_value=True):
                    try:
                        leave_service.confirm_request(123, 1)
                        if overlap:
                            assert False, "Should fail due to overlap"
                    except ValueError as e:
                        if overlap:
                            assert str(e) == "Leave request overlaps with an existing approved or confirmed leave"
                        else:
                            raise e

# --- Property 7: State Transitions ---
# Validate flow: draft -> confirm -> validate/refuse
def test_state_transitions():
    # Valid Flow
    # draft -> confirm
    with patch('app.services.leave_service.leave_service._get_request') as mock_get:
        mock_get.return_value = {
            'employee_id': [1, 'Test'], 
            'state': 'draft',
            'request_date_from': '2024-01-01',
            'request_date_to': '2024-01-02',
            'holiday_status_id': [1, 'Type'],
            'number_of_days': 1
        }
        with patch('app.services.leave_service.leave_service._check_overlap', return_value=False):
            with patch('app.services.leave_service.leave_service._check_balance', return_value=True):
                 with patch('app.services.leave_service.odoo_client.execute_kw') as mock_odoo:
                     assert leave_service.confirm_request(1, 1) is True

    # Invalid Flow: validate -> confirm
    with patch('app.services.leave_service.leave_service._get_request') as mock_get:
        mock_get.return_value = {'employee_id': [1, 'Test'], 'state': 'validate'}
        try:
             leave_service.confirm_request(1, 1)
             assert False, "Should fail transition from validate to confirm"
        except ValueError as e:
            assert "Invalid state transition" in str(e)

# --- Property 8: Balance Calculation ---
@given(allocated=st.floats(min_value=10, max_value=20), taken=st.floats(min_value=0, max_value=10))
def test_balance_calculation(allocated, taken):
    # Mock get_employees_days response
    mock_data = {
        1: { # employee_id
            10: { # leave_type_id
                'max_leaves': allocated,
                'leaves_taken': taken,
                'remaining_leaves': allocated - taken
            }
        }
    }
    
    with patch('app.services.leave_service.odoo_client.execute_kw') as mock_execute:
        mock_execute.return_value = mock_data # response for get_employees_days
        with patch('app.services.leave_service.odoo_client.search_read') as mock_search:
             mock_search.return_value = [{'id': 10, 'name': 'Paid Time Off'}]
             
             balance = leave_service.get_balance(employee_id=1)
             # Logic is essentially getting Odoo's value, but verifying our parser
             assert len(balance) == 1
             assert balance[0]['remaining'] == allocated - taken
