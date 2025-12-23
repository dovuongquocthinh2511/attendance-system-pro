# Implementation Plan - Bestmix Pro HR

## Phase 1: Backend Foundation

- [ ] 1. Set up FastAPI project structure

  - [ ] 1.1 Initialize FastAPI project with Poetry/pip
    - Create project directory structure: `app/`, `app/api/`, `app/services/`, `app/models/`, `app/core/`
    - Set up `pyproject.toml` or `requirements.txt` with dependencies: fastapi, uvicorn, sqlalchemy, pydantic, python-jose, passlib, bcrypt, hypothesis
    - Create `app/main.py` with FastAPI app instance
    - _Requirements: 5.1_
  - [ ] 1.2 Configure PostgreSQL database connection
    - Set up SQLAlchemy async engine and session
    - Create `app/core/database.py` with connection utilities
    - Create `app/core/config.py` for environment variables
    - _Requirements: 6.1_
  - [ ] 1.3 Create User model and database migration
    - Define User SQLAlchemy model in `app/models/user.py`
    - Fields: id, email, phone, password_hash, role, odoo_employee_id, is_active, created_at, updated_at
    - Create Alembic migration
    - _Requirements: 6.1, 6.2_

- [ ] 2. Implement Authentication Service

  - [ ] 2.1 Create JWT utilities
    - Implement `create_access_token()` and `verify_token()` in `app/core/security.py`
    - Token payload: sub (user_id), role, odoo_employee_id, exp
    - _Requirements: 1.1, 1.6_
  - [ ]\* 2.2 Write property test for JWT token role
    - **Property 1: JWT Token Contains Correct Role**
    - **Validates: Requirements 1.1, 1.6**
  - [ ] 2.3 Implement password hashing utilities
    - Use bcrypt for hashing in `app/core/security.py`
    - Implement `hash_password()` and `verify_password()`
    - _Requirements: 6.5_
  - [ ]\* 2.4 Write property test for password hashing
    - **Property 13: Password Hashing**
    - **Validates: Requirements 6.5**
  - [ ] 2.5 Create auth endpoints
    - `POST /auth/login` - Authenticate with email/phone + password
    - `POST /auth/logout` - Invalidate token (add to blacklist)
    - `POST /auth/refresh` - Refresh JWT token
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  - [ ]\* 2.6 Write property test for invalid credentials
    - **Property 2: Invalid Credentials Rejection**
    - **Validates: Requirements 1.2**

- [ ] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 2: Odoo Integration

- [ ] 4. Implement Odoo Proxy Service

  - [ ] 4.1 Create XML-RPC client wrapper
    - Implement `OdooClient` class in `app/services/odoo_client.py`
    - Methods: `authenticate()`, `execute_kw()`, `search_read()`, `create()`, `write()`
    - Connection pooling support
    - _Requirements: 5.1, 5.4_
  - [ ] 4.2 Implement error handling for Odoo calls
    - Create custom exceptions: `OdooConnectionError`, `OdooAPIError`
    - Log errors and return appropriate HTTP responses
    - _Requirements: 5.2, 5.3_
  - [ ] 4.3 Create Odoo model schemas
    - Define Pydantic models for Odoo data in `app/schemas/odoo.py`
    - OdooEmployee, OdooAttendance, OdooLeave, OdooLeaveType, OdooLeaveAllocation, OdooContract
    - _Requirements: 5.6, 5.7_
  - [ ]\* 4.4 Write property test for JSON serialization round-trip
    - **Property 15: JSON Serialization Round-Trip**
    - **Validates: Requirements 9.1**
  - [ ]\* 4.5 Write property test for DateTime ISO 8601 format
    - **Property 16: DateTime ISO 8601 Format**
    - **Validates: Requirements 9.3**

- [ ] 5. Implement User-Odoo Link Validation

  - [ ] 5.1 Create employee validation service
    - Implement `validate_odoo_employee_id()` in `app/services/employee_service.py`
    - Check if odoo_employee_id exists in Odoo hr.employee
    - _Requirements: 6.3_
  - [ ]\* 5.2 Write property test for User-Odoo link validation
    - **Property 12: User-Odoo Employee Link Validation**
    - **Validates: Requirements 5.6, 6.1, 6.3**

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 3: Attendance Module

- [ ] 7. Implement Attendance Service

  - [ ] 7.1 Create attendance service
    - Implement `AttendanceService` in `app/services/attendance_service.py`
    - Methods: `check_in()`, `check_out()`, `get_history()`, `get_summary()`, `get_status()`
    - _Requirements: 2.1, 2.2, 2.3, 2.7_
  - [ ] 7.2 Implement duplicate check-in prevention
    - Check for active attendance (check_out is null) before creating new
    - Return error if duplicate
    - _Requirements: 2.6_
  - [ ]\* 7.3 Write property test for duplicate check-in prevention
    - **Property 5: Duplicate Check-in Prevention**
    - **Validates: Requirements 2.6**
  - [ ] 7.4 Create attendance endpoints
    - `POST /attendance/check-in` - Create attendance record
    - `POST /attendance/check-out` - Update attendance with check_out
    - `GET /attendance/history` - Get attendance list (sorted by date desc)
    - `GET /attendance/summary` - Get monthly summary
    - `GET /attendance/status` - Get current check-in status
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 2.7_
  - [ ]\* 7.5 Write property test for attendance record consistency
    - **Property 3: Attendance Record Consistency**
    - **Validates: Requirements 2.1, 2.2**
  - [ ]\* 7.6 Write property test for attendance history ordering
    - **Property 4: Attendance History Ordering**
    - **Validates: Requirements 2.3**
  - [ ]\* 7.7 Write property test for attendance summary accuracy
    - **Property 6: Attendance Summary Accuracy**
    - **Validates: Requirements 2.7**

- [ ] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 4: Leave Module

- [ ] 9. Implement Leave Service

  - [ ] 9.1 Create leave service
    - Implement `LeaveService` in `app/services/leave_service.py`
    - Methods: `create_request()`, `confirm()`, `approve()`, `reject()`, `get_history()`, `get_balance()`, `get_types()`, `get_pending()`
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 3.6, 3.8, 3.9, 3.10, 3.11_
  - [ ] 9.2 Implement leave date validation
    - Validate: end_date >= start_date, dates not in past
    - Return validation errors
    - _Requirements: 3.5_
  - [ ]\* 9.3 Write property test for leave date validation
    - **Property 9: Leave Date Validation**
    - **Validates: Requirements 3.5**
  - [ ] 9.4 Implement leave overlap detection
    - Check for overlapping approved leaves
    - Return warning if overlap detected
    - _Requirements: 3.7_
  - [ ]\* 9.5 Write property test for leave overlap detection
    - **Property 10: Leave Overlap Detection**
    - **Validates: Requirements 3.7**
  - [ ] 9.6 Implement leave state transitions
    - Validate state flow: draft → confirm → (validate | refuse)
    - Reject invalid transitions
    - _Requirements: 3.1, 3.2, 3.8, 3.9_
  - [ ]\* 9.7 Write property test for leave state transitions
    - **Property 7: Leave Request State Transitions**
    - **Validates: Requirements 3.1, 3.2, 3.8, 3.9**
  - [ ] 9.8 Implement leave balance calculation
    - Calculate: remaining = allocated - used
    - _Requirements: 3.3_
  - [ ]\* 9.9 Write property test for leave balance calculation
    - **Property 8: Leave Balance Calculation**
    - **Validates: Requirements 3.3**
  - [ ] 9.10 Create leave endpoints
    - `POST /leave/request` - Create leave request (draft)
    - `POST /leave/{id}/confirm` - Confirm leave request
    - `POST /leave/{id}/approve` - Manager approve (validate)
    - `POST /leave/{id}/reject` - Manager reject (refuse)
    - `GET /leave/history` - Get leave history
    - `GET /leave/balance` - Get leave balance
    - `GET /leave/types` - Get leave types
    - `GET /leave/pending` - Manager: get pending requests
    - _Requirements: 3.1, 3.2, 3.3, 3.6, 3.8, 3.9, 3.10, 3.11_

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 5: Profile & User Management

- [ ] 11. Implement Profile Service

  - [ ] 11.1 Create profile service
    - Implement `ProfileService` in `app/services/profile_service.py`
    - Methods: `get_profile()`, `update_profile()`, `get_contract()`
    - _Requirements: 4.1, 4.2, 4.5_
  - [ ] 11.2 Create profile endpoints
    - `GET /profile` - Get current user profile
    - `PUT /profile` - Update allowed fields
    - `GET /profile/contract` - Get contract info
    - _Requirements: 4.1, 4.2, 4.5_

- [ ] 12. Implement User Management Service

  - [ ] 12.1 Create user management service
    - Implement `UserService` in `app/services/user_service.py`
    - Methods: `create_user()`, `update_user()`, `delete_user()`, `list_users()`, `get_team()`
    - _Requirements: 6.1, 6.2, 6.4, 6.6_
  - [ ] 12.2 Create user management endpoints
    - `GET /users` - List users (admin only)
    - `POST /users` - Create user (admin only)
    - `PUT /users/{id}` - Update user (admin only)
    - `DELETE /users/{id}` - Delete user (admin only)
    - `GET /team` - Manager: get team members
    - _Requirements: 6.1, 6.2, 6.4, 6.6_

- [ ] 13. Implement Role-Based Access Control

  - [ ] 13.1 Create RBAC middleware
    - Implement role checking decorator/dependency
    - Check JWT role against endpoint requirements
    - Return 403 for unauthorized access
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  - [ ] 13.2 Implement manager department scope
    - Filter pending leaves by manager's department
    - Filter team members by department
    - _Requirements: 3.10, 6.6_
  - [ ]\* 13.3 Write property test for RBAC
    - **Property 14: Role-Based Access Control**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
  - [ ]\* 13.4 Write property test for manager department scope
    - **Property 11: Manager Department Scope**
    - **Validates: Requirements 3.10, 6.6**

- [ ] 14. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 6: Frontend Foundation

- [ ] 15. Set up React + Vite project

  - [ ] 15.1 Initialize Vite React TypeScript project
    - Create project with `npm create vite@latest`
    - Install dependencies: react-router-dom, axios, @tanstack/react-query, fast-check
    - Set up project structure: `src/components/`, `src/pages/`, `src/services/`, `src/hooks/`, `src/types/`
    - _Requirements: 8.1_
  - [ ] 15.2 Configure PWA
    - Install vite-plugin-pwa
    - Configure service worker for static asset caching
    - Set up manifest.json
    - _Requirements: 8.2_
  - [ ] 15.3 Set up API client
    - Create axios instance with base URL and interceptors
    - Implement token refresh logic
    - Handle offline detection
    - _Requirements: 8.3, 8.5_

- [ ] 16. Implement Auth Module (Frontend)

  - [ ] 16.1 Create auth context and hooks
    - Implement `AuthContext` for global auth state
    - Create `useAuth()` hook
    - Token storage in localStorage
    - _Requirements: 1.1, 1.5_
  - [ ] 16.2 Create login page
    - Phone/email input field
    - Password input field
    - Login button with loading state
    - Error message display
    - _Requirements: 1.1, 1.2_
  - [ ] 16.3 Create protected route wrapper
    - Redirect to login if not authenticated
    - Check token expiration
    - _Requirements: 1.3_

- [ ] 17. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 7: Frontend Features

- [ ] 18. Implement Attendance Module (Frontend)

  - [ ] 18.1 Create attendance page
    - Check-in/Check-out button with status indicator
    - Current session timer (when checked in)
    - _Requirements: 2.1, 2.2, 2.5_
  - [ ] 18.2 Create attendance history component
    - List of attendance records
    - Sorted by date descending
    - _Requirements: 2.3_
  - [ ] 18.3 Create attendance summary component
    - Monthly working hours total
    - _Requirements: 2.7_

- [ ] 19. Implement Leave Module (Frontend)

  - [ ] 19.1 Create leave request form
    - Leave type selector
    - Date range picker
    - Description input
    - Submit and confirm buttons
    - _Requirements: 3.1, 3.2, 3.11_
  - [ ] 19.2 Create leave balance component
    - Display allocated, used, remaining days per type
    - _Requirements: 3.3_
  - [ ] 19.3 Create leave history component
    - List of leave requests with status
    - Status badges (draft, confirm, validate, refuse)
    - _Requirements: 3.6_
  - [ ] 19.4 Create manager approval page
    - List of pending requests
    - Approve/Reject buttons
    - _Requirements: 3.8, 3.9, 3.10_

- [ ] 20. Implement Profile Module (Frontend)

  - [ ] 20.1 Create profile page
    - Display employee info from Odoo
    - Edit form for allowed fields
    - _Requirements: 4.1, 4.2_
  - [ ] 20.2 Create contract info component
    - Display contract details (read-only)
    - _Requirements: 4.5_

- [ ] 21. Implement Admin Module (Frontend)

  - [ ] 21.1 Create user management page
    - User list table
    - Create/Edit user modal
    - Delete confirmation
    - _Requirements: 6.1, 6.2, 6.4_
  - [ ] 21.2 Create team view page
    - List of team members for managers
    - _Requirements: 6.6_

- [ ] 22. Implement Offline Handling

  - [ ] 22.1 Create offline indicator component
    - Show banner when offline
    - Disable data operations
    - _Requirements: 8.3, 8.5_

- [ ] 23. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
