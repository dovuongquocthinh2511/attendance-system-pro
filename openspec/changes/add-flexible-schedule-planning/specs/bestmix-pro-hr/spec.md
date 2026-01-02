## ADDED Requirements

### Requirement: Planning Schedule Integration

**User Story:** As an employee, I want to view my work schedule from the Planning module, so that I know when I am expected to work including dynamic days like specific Saturdays.

#### Acceptance Criteria

1. WHEN an employee views their schedule THEN the system SHALL display shifts from Odoo planning.slot for the current and upcoming week
2. WHEN an employee has a shift scheduled for today THEN the system SHALL display shift start/end times on the attendance screen
3. WHEN an employee views schedule history THEN the system SHALL display past shifts for the previous 7 days
4. WHEN a shift is published in Odoo Planning THEN the system SHALL reflect the shift when employee refreshes schedule
5. IF no shifts are scheduled for a day THEN the system SHALL indicate it as a non-working day

#### Scenario: View upcoming schedule
- **GIVEN** employee has shifts scheduled for the week
- **WHEN** employee opens schedule view
- **THEN** system displays all shifts for next 7 days with start/end times

#### Scenario: View today's shift on attendance screen
- **GIVEN** employee has a shift today 8AM-5PM
- **WHEN** employee opens attendance screen
- **THEN** system displays "Scheduled: 8:00 AM - 5:00 PM"

#### Scenario: No shift scheduled
- **GIVEN** employee has no shift for Saturday
- **WHEN** employee views schedule for Saturday
- **THEN** system indicates "No shift scheduled"

### Requirement: Flexible Schedule Support

**User Story:** As an HR admin, I want to configure employees with flexible working hours, so that they can work dynamic schedules like only 2 Saturdays per month.

#### Acceptance Criteria

1. WHEN an employee has flexible_hours enabled in Odoo THEN the system SHALL validate attendance against planning.slot shifts instead of fixed calendar
2. WHEN an employee with flexible schedule checks in without a scheduled shift THEN the system SHALL allow check-in with a warning message
3. WHEN an employee has work_entry_source='planning' in contract THEN the system SHALL use planning.slot for attendance validation
4. WHEN viewing attendance summary THEN the system SHALL compare actual hours against planned shift hours

#### Scenario: Flexible employee checks in with shift
- **GIVEN** employee has flexible_hours=True and shift today
- **WHEN** employee checks in
- **THEN** system validates successfully and creates attendance

#### Scenario: Flexible employee checks in without shift
- **GIVEN** employee has flexible_hours=True and no shift today
- **WHEN** employee checks in
- **THEN** system allows check-in with warning "No scheduled shift"

#### Scenario: Attendance summary with planning
- **GIVEN** employee has work_entry_source='planning'
- **WHEN** employee views monthly summary
- **THEN** system shows actual hours vs planned hours from shifts

## MODIFIED Requirements

### Requirement: Online Attendance (Chấm công)

**User Story:** As an employee, I want to check in and check out online, so that I can record my working hours without physical time clock.

#### Acceptance Criteria

1. WHEN an employee performs check-in THEN the system SHALL create hr.attendance record in Odoo with check_in timestamp
2. WHEN an employee performs check-out THEN the system SHALL update hr.attendance record in Odoo with check_out timestamp
3. WHEN an employee views attendance history THEN the system SHALL display records from Odoo hr.attendance sorted by date descending
4. IF the Odoo API call fails THEN the system SHALL return error immediately and prompt user to retry
5. WHILE an employee has an active check-in (no check_out) THEN the system SHALL display the current session duration
6. WHEN an employee attempts duplicate check-in without check-out THEN the system SHALL prevent the action and display a warning
7. WHEN an employee views attendance summary THEN the system SHALL display total working hours for current month
8. WHEN an employee with flexible schedule checks in THEN the system SHALL validate against planning.slot if work_entry_source is 'planning'
9. WHEN check-in occurs outside scheduled shift hours THEN the system SHALL log a warning but allow the check-in

#### Scenario: Check-in with scheduled shift
- **GIVEN** employee has a planning.slot for today 8AM-5PM
- **WHEN** employee checks in at 8:05 AM
- **THEN** system creates hr.attendance with check_in timestamp
- **AND** response includes shift_info with scheduled times

#### Scenario: Check-in without scheduled shift (flexible employee)
- **GIVEN** employee has flexible_hours=True and no shift today
- **WHEN** employee checks in
- **THEN** system creates hr.attendance with check_in timestamp
- **AND** response includes warning "No scheduled shift found"

#### Scenario: Check-in without shift (fixed schedule employee)
- **GIVEN** employee has flexible_hours=False and work_entry_source='calendar'
- **WHEN** employee checks in on non-working day (per calendar)
- **THEN** system validates against resource.calendar as before

#### Scenario: Check-out updates attendance
- **GIVEN** employee has active check-in
- **WHEN** employee checks out
- **THEN** system updates hr.attendance with check_out timestamp

#### Scenario: View attendance history
- **GIVEN** employee has attendance records
- **WHEN** employee views history
- **THEN** records are sorted by check_in date descending

### Requirement: Odoo Integration (Version 18.0)

**User Story:** As a system administrator, I want the backend to securely communicate with Odoo 18.0, so that HR data is stored directly in Odoo.

#### Acceptance Criteria

1. WHEN the backend initializes THEN the system SHALL validate the Odoo admin API key connectivity via XML-RPC
2. WHEN an API call to Odoo fails THEN the system SHALL log the error and return error to user immediately
3. WHEN the Odoo connection is unavailable THEN the system SHALL return error to user (no local caching for attendance/leave data)
4. WHILE processing Odoo requests THEN the system SHALL use connection pooling to optimize performance
5. WHEN sensitive data is transmitted THEN the system SHALL encrypt the communication channel
6. WHEN mapping local user to Odoo THEN the system SHALL use odoo_employee_id field to link with hr.employee
7. WHEN creating attendance or leave records THEN the system SHALL write directly to Odoo (hr.attendance, hr.leave) without local storage
8. WHEN fetching employee schedule THEN the system SHALL read from planning.slot model with employee_id filter
9. WHEN fetching shift data THEN the system SHALL include role information from planning.role if available

#### Scenario: Fetch employee shifts
- **GIVEN** employee has odoo_employee_id=42
- **WHEN** backend requests schedule for date range
- **THEN** system queries planning.slot with employee_id=42 filter
- **AND** returns shift list with start/end times and role info

#### Scenario: Backend initialization
- **GIVEN** backend starts up
- **WHEN** initializing Odoo connection
- **THEN** system validates API key connectivity via XML-RPC

#### Scenario: Odoo API failure
- **GIVEN** Odoo server is unavailable
- **WHEN** API call is made
- **THEN** system logs error and returns error to user immediately
