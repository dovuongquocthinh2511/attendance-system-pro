from hypothesis import given, strategies as st
from unittest.mock import MagicMock, patch
from app.services.employee_service import employee_service

# --- Property 12: User-Odoo Employee Link Validation ---
# Validates Requirements 5.6, 6.1, 6.3
@given(odoo_id=st.integers(min_value=1))
def test_validate_odoo_employee_id(odoo_id):
    # Mock the odoo_client within the service module
    with patch('app.services.employee_service.odoo_client') as mock_client:
        # Case 1: Odoo returns count > 0 (Exists)
        mock_client.execute_kw.return_value = 1
        assert employee_service.validate_odoo_employee_id(odoo_id) is True
        
        # Case 2: Odoo returns count = 0 (Not Exists)
        mock_client.execute_kw.return_value = 0
        assert employee_service.validate_odoo_employee_id(odoo_id) is False
        
        # Case 3: Exception (Connection Error) -> Should return False (safe fail)
        mock_client.execute_kw.side_effect = Exception("Connection Failed")
        assert employee_service.validate_odoo_employee_id(odoo_id) is False

        # Case 4: ID is None or 0 -> Should return False immediately without calling Odoo
        if not odoo_id:
             # Reset mock to ensure we don't count previous calls
            mock_client.reset_mock()
            assert employee_service.validate_odoo_employee_id(None) is False
            assert employee_service.validate_odoo_employee_id(0) is False
