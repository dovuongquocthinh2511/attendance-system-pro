# Requirements Document

## Introduction

Bestmix Pro là hệ thống quản lý nhân sự nội bộ dành cho nhân viên Bestmix. Hệ thống cung cấp các chức năng chấm công online, xin nghỉ phép và quản lý hồ sơ cá nhân. Kiến trúc hệ thống bao gồm:
- Frontend: ReactJS + Vite (Mobile-first PWA)
- Backend: FastAPI + Python (proxy pattern)
- Database: PostgreSQL (lưu user info, API keys)
- Integration: Odoo nội bộ qua XML-RPC

Backend hoạt động như một proxy layer, sử dụng admin API key để giao tiếp với Odoo, giúp tiết kiệm chi phí license Odoo user.

## Odoo Integration Reference

### Odoo Models

| Model | Mô tả | Fields quan trọng |
|-------|-------|-------------------|
| `hr.employee` | Thông tin nhân viên | `id`, `name`, `work_email`, `department_id`, `job_id`, `parent_id`, `mobile_phone`, `birthday`, `identification_id`, `barcode` |
| `hr.attendance` | Chấm công | `id`, `employee_id`, `check_in`, `check_out`, `worked_hours` |
| `hr.leave` | Đơn nghỉ phép | `id`, `employee_id`, `holiday_status_id`, `request_date_from`, `request_date_to`, `state`, `number_of_days`, `name` |
| `hr.leave.type` | Loại nghỉ phép | `id`, `name`, `allocation_type`, `max_leaves`, `leaves_taken`, `remaining_leaves` |
| `hr.leave.allocation` | Phân bổ ngày phép | `id`, `employee_id`, `holiday_status_id`, `number_of_days`, `state` |
| `hr.contract` | Hợp đồng | `id`, `employee_id`, `name`, `wage`, `state`, `date_start`, `date_end`, `job_id`, `department_id` |
| `hr.department` | Phòng ban | `id`, `name`, `manager_id`, `parent_id` |
| `hr.job` | Vị trí công việc | `id`, `name`, `department_id` |

### Odoo API Reference

- **XML-RPC Endpoint**: `/xmlrpc/2/object`
- **Method**: `execute_kw(db, uid, password, model, method, args, kwargs)`
- **Attendance Methods**: 
  - `create` - Tạo record attendance mới
  - `write` - Cập nhật check_out
  - `search_read` - Lấy danh sách attendance
  - `attendance_manual` - Check-in/out thủ công (nếu có quyền)
- **Leave States**: `draft` → `confirm` → `validate` / `refuse`
- **Contract States**: `draft`, `open`, `close`, `cancel`

## Glossary

- **Bestmix Pro**: Hệ thống quản lý nhân sự nội bộ
- **Employee**: Nhân viên sử dụng hệ thống (có 3 roles: employee, manager, admin)
- **Attendance**: Bản ghi chấm công (check-in/check-out)
- **Leave Request**: Đơn xin nghỉ phép
- **Odoo**: Hệ thống ERP nội bộ (version 18.0) chứa dữ liệu HR master
- **XML-RPC**: Giao thức giao tiếp với Odoo API
- **PWA**: Progressive Web App - ứng dụng web có thể cài đặt như app native
- **Backend Proxy**: Layer trung gian xử lý authentication và forward request tới Odoo
- **Local Employee**: Bản ghi employee trong backend DB, liên kết với hr.employee qua odoo_employee_id
- **Role**: Phân quyền người dùng (employee, manager, admin)

## Requirements

### Requirement 1: User Authentication

**User Story:** As an employee, I want to log in to the system using my phone number or email, so that I can access HR features securely.

#### Acceptance Criteria

1. WHEN an employee submits valid phone number or email with correct password THEN the system SHALL authenticate the user against the local database and return a JWT token
2. WHEN an employee submits invalid credentials THEN the system SHALL reject the login attempt and return an error message within 2 seconds
3. WHEN a JWT token expires THEN the system SHALL require the user to re-authenticate
4. WHEN an employee logs out THEN the system SHALL invalidate the current session token
5. WHILE a user session is active THEN the system SHALL refresh the token automatically before expiration
6. WHEN a user authenticates successfully THEN the system SHALL include user role (employee, manager, admin) in the JWT token payload

### Requirement 2: Online Attendance (Chấm công)

**User Story:** As an employee, I want to check in and check out online, so that I can record my working hours without physical time clock.

#### Acceptance Criteria

1. WHEN an employee performs check-in THEN the system SHALL create hr.attendance record in Odoo with check_in timestamp
2. WHEN an employee performs check-out THEN the system SHALL update hr.attendance record in Odoo with check_out timestamp
3. WHEN an employee views attendance history THEN the system SHALL display records from Odoo hr.attendance sorted by date descending
4. IF the Odoo API call fails THEN the system SHALL return error immediately and prompt user to retry
5. WHILE an employee has an active check-in (no check_out) THEN the system SHALL display the current session duration
6. WHEN an employee attempts duplicate check-in without check-out THEN the system SHALL prevent the action and display a warning
7. WHEN an employee views attendance summary THEN the system SHALL display total working hours for current month

### Requirement 3: Leave Request (Xin nghỉ phép)

**User Story:** As an employee, I want to submit leave requests online, so that I can request time off without paperwork.

#### Acceptance Criteria

1. WHEN an employee submits a leave request THEN the system SHALL create the request in Odoo hr.leave with draft status
2. WHEN an employee confirms a draft leave request THEN the system SHALL update hr.leave state to confirm in Odoo
3. WHEN an employee views leave balance THEN the system SHALL display allocated days, used days, and remaining days from Odoo hr.leave.allocation
4. WHEN a leave request status changes in Odoo THEN the system SHALL reflect the updated status when user refreshes
5. WHEN an employee submits a leave request with invalid dates THEN the system SHALL reject the request and display validation errors
6. WHEN an employee views leave history THEN the system SHALL display all requests with status (draft, confirm, validate, refuse) from Odoo
7. IF the leave request overlaps with existing approved leave THEN the system SHALL warn the user before submission
8. WHEN a manager approves a leave request THEN the system SHALL update the hr.leave state to validate in Odoo
9. WHEN a manager rejects a leave request THEN the system SHALL update the hr.leave state to refuse in Odoo
10. WHEN a manager views pending leave requests THEN the system SHALL display requests with state confirm from employees in their department
11. WHEN an employee views leave types THEN the system SHALL display available leave types from Odoo hr.leave.type

### Requirement 4: Employee Profile Management

**User Story:** As an employee, I want to view and update my personal information, so that I can keep my HR records accurate.

#### Acceptance Criteria

1. WHEN an employee views their profile THEN the system SHALL display personal information synced from Odoo
2. WHEN an employee updates allowed profile fields THEN the system SHALL save changes to Odoo and confirm success
3. WHEN profile sync from Odoo fails THEN the system SHALL display cached data with a sync status indicator
4. WHILE profile data is being synced THEN the system SHALL display a loading indicator
5. WHEN an employee views their profile THEN the system SHALL display contract information (read-only) from Odoo

### Requirement 5: Odoo Integration (Version 18.0)

**User Story:** As a system administrator, I want the backend to securely communicate with Odoo 18.0, so that HR data is stored directly in Odoo.

#### Acceptance Criteria

1. WHEN the backend initializes THEN the system SHALL validate the Odoo admin API key connectivity via XML-RPC
2. WHEN an API call to Odoo fails THEN the system SHALL log the error and return error to user immediately
3. WHEN the Odoo connection is unavailable THEN the system SHALL return error to user (no local caching for attendance/leave data)
4. WHILE processing Odoo requests THEN the system SHALL use connection pooling to optimize performance
5. WHEN sensitive data is transmitted THEN the system SHALL encrypt the communication channel
6. WHEN mapping local user to Odoo THEN the system SHALL use odoo_employee_id field to link with hr.employee
7. WHEN creating attendance or leave records THEN the system SHALL write directly to Odoo (hr.attendance, hr.leave) without local storage

### Requirement 6: User & Employee Management

**User Story:** As an admin, I want to manage user accounts linked to Odoo employees, so that employees can access the system without Odoo licenses.

#### Acceptance Criteria

1. WHEN an admin creates a new user THEN the system SHALL store user credentials in local database with link to odoo_employee_id
2. WHEN an admin assigns a role to a user THEN the system SHALL update the user role (employee, manager, admin) in local database
3. WHEN a user record is created THEN the system SHALL validate that odoo_employee_id exists in Odoo hr.employee
4. WHEN viewing user list THEN the system SHALL display user info merged with Odoo employee data
5. WHEN an admin updates user password THEN the system SHALL hash the password using bcrypt before storing
6. WHEN a manager views their team THEN the system SHALL display employees under their department from Odoo

### Requirement 7: Role-Based Access Control

**User Story:** As a system administrator, I want to control access based on user roles, so that sensitive operations are restricted appropriately.

#### Acceptance Criteria

1. WHEN an employee accesses the system THEN the system SHALL allow viewing own attendance, leave requests, and profile only
2. WHEN a manager accesses the system THEN the system SHALL allow viewing team attendance and approving leave requests for their department
3. WHEN an admin accesses the system THEN the system SHALL allow full access to all features including user management
4. WHEN a user attempts unauthorized action THEN the system SHALL reject the request and return 403 Forbidden
5. WHILE processing API requests THEN the system SHALL validate user role from JWT token before executing

### Requirement 8: Mobile-First PWA

**User Story:** As an employee, I want to use the system on my mobile device, so that I can access HR features anywhere.

#### Acceptance Criteria

1. WHEN the application loads on mobile THEN the system SHALL render a responsive mobile-optimized interface
2. WHEN a user installs the PWA THEN the system SHALL cache static assets for faster loading
3. WHEN the device is offline THEN the system SHALL display offline indicator and disable data operations
4. WHEN a push notification is enabled THEN the system SHALL notify users of leave request status changes
5. WHILE offline THEN the system SHALL display clear indicators that features require internet connection

### Requirement 9: Data Serialization

**User Story:** As a developer, I want consistent data serialization between frontend and backend, so that data integrity is maintained across the system.

#### Acceptance Criteria

1. WHEN the backend serializes data to JSON THEN the system SHALL produce valid JSON that can be deserialized back to equivalent objects
2. WHEN the frontend receives API responses THEN the system SHALL parse JSON data into typed objects
3. WHEN date/time values are serialized THEN the system SHALL use ISO 8601 format with timezone information
