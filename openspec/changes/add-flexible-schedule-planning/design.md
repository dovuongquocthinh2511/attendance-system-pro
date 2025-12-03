# Design: Flexible Schedule with Planning Module Integration

## Context
Bestmix Pro cần hỗ trợ nhân viên có lịch làm việc linh hoạt (dynamic Saturday scheduling). Odoo 18 Enterprise đã có Planning module native, đây là giải pháp best practice thay vì custom development.

**Stakeholders:**
- HR Admin: Cấu hình lịch làm việc trong Odoo
- Manager: Tạo và assign shifts qua Planning module
- Employee: Xem schedule và check-in/out qua Bestmix Pro PWA

## Goals / Non-Goals

**Goals:**
- Tích hợp Odoo Planning module vào Bestmix Pro
- Hỗ trợ flexible/dynamic scheduling (ví dụ: 2/4 thứ 7 trong tháng)
- Validate attendance dựa trên assigned shifts
- Hiển thị upcoming shifts cho employees trên PWA

**Non-Goals:**
- Tạo/edit shifts từ Bestmix Pro (sử dụng Odoo UI)
- Replace hoàn toàn resource.calendar (vẫn dùng cho base schedule)
- Auto-scheduling logic trong backend

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Bestmix Pro Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │   Frontend   │────▶│   Backend    │────▶│   Odoo 18    │   │
│  │     PWA      │     │   FastAPI    │     │  Enterprise  │   │
│  └──────────────┘     └──────────────┘     └──────────────┘   │
│         │                    │                    │            │
│         │              ┌─────┴─────┐        ┌─────┴─────┐     │
│         │              │           │        │           │     │
│    View Shifts    Planning    Attendance   planning   hr.     │
│    Check-in/out   Service     Service      .slot    attendance│
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

### Odoo Configuration Model

```
Employee Setup:
├── hr.employee
│   ├── flexible_hours: True
│   └── resource_calendar_id: "Flexible 40h/week"
│
├── hr.contract
│   ├── work_entry_source: 'planning'  # Critical!
│   └── resource_calendar_id: linked
│
└── planning.slot (created by Manager)
    ├── Mon-Fri: Recurring weekly shifts
    └── Saturday: Specific date shifts only
```

### Data Flow

```
1. Manager creates shifts in Odoo Planning
   └── planning.slot records created

2. Employee opens Bestmix Pro PWA
   └── Backend fetches planning.slot via XML-RPC
       └── Frontend displays upcoming shifts

3. Employee checks in
   └── Backend validates against planning.slot
       ├── Has shift? → Create hr.attendance
       └── No shift? → Warning (allow with flag)

4. Payroll calculation
   └── Odoo uses planning.slot (work_entry_source='planning')
```

## Decisions

### Decision 1: Read-only Planning Integration
**What:** Backend chỉ đọc `planning.slot`, không tạo/edit
**Why:** 
- Manager sử dụng Odoo UI (Gantt chart, drag-drop) để scheduling
- Tránh duplicate logic và potential conflicts
- Odoo UI đã có auto-plan, shift templates

### Decision 2: Attendance Validation Strategy
**What:** Soft validation - warn nhưng vẫn cho check-in khi không có shift
**Why:**
- Tránh block employee trong trường hợp manager quên tạo shift
- Log warning để HR review
- Có thể configure strict mode sau nếu cần

### Decision 3: Shift Display Scope
**What:** Hiển thị shifts 7 ngày tới + 7 ngày qua
**Why:**
- Đủ context cho employee plan work
- Không quá nhiều data
- Có thể expand nếu cần

## Odoo Models Reference (New)

### planning.slot
| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Primary key |
| `employee_id` | Many2one | Link to hr.employee |
| `resource_id` | Many2one | Link to resource.resource |
| `role_id` | Many2one | Link to planning.role |
| `start_datetime` | datetime | Shift start time |
| `end_datetime` | datetime | Shift end time |
| `allocated_hours` | float | Planned hours |
| `state` | selection | draft/published/canceled |
| `repeat` | boolean | Is recurring |
| `repeat_type` | selection | daily/weekly/monthly |

### planning.role
| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Primary key |
| `name` | str | Role name |
| `color` | int | UI color |

## API Design

### New Endpoints

```python
# GET /schedule/shifts
# Get employee's shifts within date range
Request:
  - date_from: date (default: today - 7 days)
  - date_to: date (default: today + 7 days)

Response:
  - shifts: List[Shift]
    - id: int
    - start_datetime: datetime (ISO 8601)
    - end_datetime: datetime (ISO 8601)
    - allocated_hours: float
    - role_name: str | None
    - state: str

# GET /schedule/today
# Get today's shift (if any)
Response:
  - has_shift: bool
  - shift: Shift | None
  - is_flexible: bool
```

### Updated Attendance Response

```python
# POST /attendance/check-in
Response (updated):
  - success: bool
  - attendance_id: int
  - check_in: datetime
  - shift_info: ShiftInfo | None  # NEW
    - shift_id: int
    - scheduled_start: datetime
    - scheduled_end: datetime
  - warning: str | None  # NEW - "No scheduled shift found"
```

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Manager quên tạo shift | Employee không thấy schedule | Soft validation, weekly reminder |
| Odoo Planning license cost | Đã có Enterprise | N/A - included |
| Sync delay | Shift mới không hiển thị ngay | Cache TTL 5 phút, manual refresh |
| Complex recurring patterns | Khó setup | Provide templates, documentation |

## Migration Plan

1. **Phase 1: Backend** (Week 1)
   - Add Planning service
   - Update Attendance validation
   - Deploy to staging

2. **Phase 2: Frontend** (Week 2)
   - Add shift display components
   - Update Attendance UI
   - User testing

3. **Phase 3: Odoo Config** (Week 2-3)
   - Configure flexible schedules
   - Train managers on Planning module
   - Create shift templates

4. **Rollback:**
   - Disable shift validation flag
   - Hide schedule UI components
   - Revert to calendar-only validation

## Open Questions

1. ~~Should we cache planning.slot locally?~~ → No, always fetch from Odoo for consistency
2. ~~Strict vs soft validation?~~ → Start with soft, make configurable
3. Notification cho shift changes? → Future enhancement (Phase 2)
