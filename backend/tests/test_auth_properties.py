from hypothesis import given, strategies as st, settings
from app.core import security
from app.models.user import User

# --- Property 1: JWT Token Contains Correct Role ---
# Validates Requirements 1.1, 1.6
@given(
    role=st.sampled_from(["admin", "manager", "employee"]),
    user_id=st.integers(min_value=1),
    odoo_id=st.integers(min_value=1)
)
def test_jwt_contains_correct_role(role, user_id, odoo_id):
    # Setup
    data = {"sub": str(user_id), "role": role, "odoo_employee_id": odoo_id}
    
    # Action: Create token
    token = security.create_access_token(data=data)
    
    # Verification: Decode token
    payload = security.verify_token(token)
    
    # Assert
    assert payload.role == role
    assert payload.sub == str(user_id)
    assert payload.odoo_employee_id == odoo_id


# --- Property 13: Password Hashing ---
# Validates Requirements 6.5
# Disable deadline because bcrypt is intentionally slow
@settings(deadline=None)
@given(password=st.text(min_size=1).filter(lambda x: "\0" not in x))
def test_password_hashing_consistency(password):
    # Action 1: Hash password
    hashed = security.hash_password(password)
    
    # Assert 1: Hash is not the password itself
    assert hashed != password
    
    # Assert 2: Verify returns True for correct password
    assert security.verify_password(password, hashed) is True
    
    # Assert 3: Verify returns False for incorrect password
    assert security.verify_password(password + "wrong", hashed) is False


# --- Property 2: Invalid Credentials Rejection ---
# Validates Requirements 1.2
# Note: Testing full endpoint logic would require DB mocking which is complex for property tests.
# Here we test the verification logic if we had a user.
@settings(deadline=None)
@given(
    real_password=st.text(min_size=5).filter(lambda x: "\0" not in x),
    wrong_password=st.text(min_size=5).filter(lambda x: "\0" not in x)
)
def test_invalid_credential_check(real_password, wrong_password):
    # Assume they are different
    if real_password == wrong_password:
        return

    # Setup
    hashed = security.hash_password(real_password)
    
    # Verify rejection
    assert security.verify_password(wrong_password, hashed) is False
