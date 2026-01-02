from hypothesis import given, strategies as st
from datetime import datetime
import json
from pydantic.json import pydantic_encoder
from app.schemas.odoo import OdooAttendance, OdooEmployee

# --- Property 15: JSON Serialization Round-Trip ---
# Validates Requirements 9.1
# Ensures that Pydantic models (used for Odoo data) can be serialized to JSON.
@given(
    id_val=st.integers(),
    name_val=st.text(),
    # Create dictionary representing JSON object, but simple types
    # or just verifying Pydantic models can dump to json
)
def test_json_serialization_round_trip(id_val, name_val):
    # Setup: Create an OdooEmployee object
    employee = OdooEmployee(id=id_val, name=name_val)
    
    # Action: Serialize to JSON string
    # FastAPI uses pydantic's default encoding or json.dumps with default=pydantic_encoder
    json_str = json.dumps(employee.model_dump(), default=pydantic_encoder)
    
    # Action: Deserialize back
    data = json.loads(json_str)
    
    # Assert
    assert data["id"] == id_val
    assert data["name"] == name_val


# --- Property 16: DateTime ISO 8601 Format ---
# Validates Requirements 9.3
# Odoo returns strings in UTC usually, but Pydantic handles datetime. 
# We test that our schema handles serialization correctly.
@given(
    check_in=st.datetimes(),
    check_out=st.datetimes()
)
def test_datetime_iso_8601(check_in, check_out):
    # Setup
    if check_out < check_in:
        return # Skip invalid range logic, just testing format here
        
    attendance = OdooAttendance(
        id=1, 
        employee_id=[1, "Name"],
        check_in=check_in,
        check_out=check_out
    )
    
    # Action: Serialize
    json_str = json.dumps(attendance.model_dump(), default=str)
    # Note: pydantic_encoder or str often used for datetime
    
    # Verify it looks like ISO string in JSON
    # It should be something like "2023-01-01T..."
    # A simple check is that we can parse it back
    data = json.loads(json_str)
    
    # Re-parse string to datetime
    parsed_in = datetime.fromisoformat(data["check_in"])
    parsed_out = datetime.fromisoformat(data["check_out"])
    
    assert parsed_in == check_in
    assert parsed_out == check_out
