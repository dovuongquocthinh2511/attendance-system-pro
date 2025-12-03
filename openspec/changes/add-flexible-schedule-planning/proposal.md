# Change: Add Flexible Schedule with Planning Module Integration

## Why
Nhân viên có lịch làm việc dynamic (ví dụ: chỉ làm 2/4 thứ 7 trong tháng) không thể được quản lý bằng `resource.calendar` cố định trong contract. Cần tích hợp Odoo 18 Planning module để hỗ trợ scheduling linh hoạt, đồng thời cập nhật Bestmix Pro backend để sync và validate attendance dựa trên shifts.

## What Changes
- **ADDED**: Odoo Planning models (`planning.slot`, `planning.role`) vào integration reference
- **ADDED**: Planning Schedule Service trong backend để đọc shifts từ Odoo
- **ADDED**: Endpoint hiển thị upcoming shifts cho employees
- **MODIFIED**: Attendance validation logic để check against planning shifts
- **MODIFIED**: Employee profile để hiển thị lịch làm việc từ Planning
- **ADDED**: Flexible schedule configuration guide trong Odoo setup

## Impact
- Affected specs: `bestmix-pro-hr` (requirements + design)
- Affected code: 
  - Backend: `attendance_service.py`, `odoo_proxy.py` (new planning methods)
  - Frontend: `AttendanceModule`, `ProfileModule` (shift display)
- Dependencies: Odoo 18 Enterprise Planning module (đã có)

## Technical Approach
Sử dụng native Odoo 18 Planning module:
1. Configure `flexible_hours = True` trên employee
2. Contract `work_entry_source = 'planning'`
3. Manager tạo shifts trong Planning module (recurring cho Mon-Fri, specific dates cho Saturday)
4. Backend proxy đọc `planning.slot` để validate attendance và hiển thị schedule

## Benefits
- Zero custom development cho scheduling logic
- Enterprise-grade UI sẵn có trong Odoo
- Auto-sync với Payroll, Attendance, Time Off
- Mobile-ready cho employees
- Reporting & analytics built-in
