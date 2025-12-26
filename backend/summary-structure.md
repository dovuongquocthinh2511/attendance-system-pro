# Cấu Trúc Dự Án Backend Bestmix Pro HR

Tài liệu này giải thích cách tổ chức mã nguồn (Project Structure) của backend project, nhằm giúp lập trình viên hiểu rõ vai trò và trách nhiệm của từng thư mục/file.

Mô hình áp dụng: **Layered Architecture (Service Pattern)** kết hợp với **FastAPI**.

## Cây Thư Mục Tổng Quát

```
backend/
├── app/
│   ├── api/                # Layer giao tiếp (Controller)
│   │   ├── deps.py         # Dependencies (Injection, Auth, RoleChecker)
│   │   └── endpoints/      # Định nghĩa các API Routes
│   ├── services/           # Layer nghiệp vụ (Business Logic)
│   ├── models/             # Layer dữ liệu (Database Models)
│   ├── schemas/            # Layer xác thực dữ liệu (Pydantic Models / DTOs)
│   ├── core/               # Cấu hình & Tiện ích lõi
│   └── main.py             # Entrypoint khởi chạy ứng dụng
├── tests/                  # Thư mục chứa Tests
│   ├── conftest.py         # Fixtures cho Pytest
│   └── ...                 # Các file test
├── scripts/                # Scripts tiện ích (vd: test connect)
└── requirements.txt        # Danh sách thư viện
```

## Chi Tiết Các Thành Phần

### 1. `app/api/` (Presentation Layer)

Nơi tiếp nhận request từ Client, validate input cơ bản và gọi xuống Service layer. Tuyệt đối **không** viết logic nghiệp vụ phức tạp ở đây.

- **`endpoints/`**:
  - `auth.py`: Các API login, logout, refresh token.
  - `users.py`: Các API tạo mới, lấy danh sách user.
  - `attendance.py`: Các API Check-in/out, xem lịch sử, tổng hợp công.
  - `leave.py`: Các API xin nghỉ phép, duyệt đơn, xem phép tồn.
  - `profile.py`: Các API xem/sửa profile, hợp đồng.
- **`deps.py`**:
  - `get_db`: Lấy session DB.
  - `get_current_user`: Xác thực token/blacklist.
  - `RoleChecker`: Class kiểm tra phân quyền (RBAC).

### 2. `app/services/` (Business Logic Layer)

Trái tim của ứng dụng. Chứa toàn bộ logic xử lý nghiệp vụ. Controller (API) chỉ việc gọi hàm trong đây.

- **`user_service.py`**: Logic User (create, validation, get_team).
- **`auth_service.py`**: Logic Auth (login, logout, token gen, blacklist).
- **`odoo_client.py`**: Service kết nối và giao tiếp XML-RPC với Odoo ERP.
- **`employee_service.py`**: Service xử lý logic Employee, validate ID với Odoo.
- **`attendance_service.py`**: Service logic chấm công (Check-in, Check-out, History, Summary).
- **`leave_service.py`**: Service logic nghỉ phép (Tạo đơn, Duyệt, Validate ngày, Check trùng, Phép tồn).
- **`profile_service.py`**: Service logic Profile (Get Profile, Update Whitelisted Fields, Contract).

### 3. `app/models/` (Data Access Layer)

Định nghĩa các bảng (Tables) trong Database sử dụng SQLAlchemy ORM.

- **`user.py`**: Bảng `users` (lưu info, password hash, role, link Odoo ID).
- **`token_blacklist.py`**: Bảng `token_blacklist` (lưu các token đã đăng xuất).

### 4. `app/schemas/` (Data Transfer Objects)

Định nghĩa cấu trúc dữ liệu Input/Output (Pydantic Models).

- **`user.py`**: Login, Create, Response schemas, UserUpdate.
- **`token.py`**: JWT Token schemas.
- **`odoo.py`**: Schemas cho dữ liệu Odoo (`OdooEmployee`, `OdooAttendance`).
- **`attendance.py`**: Schemas chấm công (`AttendanceCheckIn`, `AttendanceStatus`, `AttendanceSummary`).
- **`leave.py`**: Schemas nghỉ phép (`LeaveRequestCreate`).
- **`profile.py`**: Schemas cập nhật hồ sơ (`ProfileUpdate`).
- **`common.py`**: Các schema dùng chung (`ActionResponse` cho các action thành công/thất bại).
- **`response.py`**: Generic Wrapper `APIResponse` chuẩn hóa toàn bộ phản hồi API.

### 5. `app/core/` (Core Utilities)

Chứa các thành phần nòng cốt, cấu hình hệ thống và xử lý lỗi.

- **`config.py`**: Quản lý biến môi trường (DB, Secret Key, Odoo Config).
- **`database.py`**: Kết nối Database, retry logic.
- **`security.py`**: Tiện ích bảo mật (Hash, Verify Pass/Token).
- **`exceptions.py`**: (New) Các Custom Exceptions (`OdooAPIError`, `DuplicateCheckinError`, `LeaveOverlapError`...) và Error Codes chuẩn.

### 6. `backend/tests/` (Testing)

Thư mục chứa các bài test tự động (Property-based tests).

- **`conftest.py`**: Cấu hình môi trường test, DB ảo.
- **`test_auth_properties.py`**: Test logic Auth, Hash, Token.
- **`test_odoo_properties.py`**: Test logic serialize dữ liệu Odoo.
- **`test_validation_property.py`**: Test logic validate User-Odoo link.
- **`test_attendance_properties.py`**: Test logic chấm công (Check-in trùng, Consistency, Summary).
- **`test_leave_properties.py`**: Test logic nghỉ phép (Validate ngày, Check trùng, State transition, Balance).
- **`test_rbac_properties.py`**: Test logic phân quyền (Admin Access, Manager Scope).

---

**Lợi ích của cấu trúc này:**

- **Tách biệt trách nhiệm (Separation of Concerns)**: Logic không bị trộn lẫn, dễ bảo trì.
- **Dễ mở rộng (Scalable)**: Thêm tính năng mới chỉ cần thêm Service và Endpoint tương ứng.
- **Dễ test**: Có thể viết Unit Test cho từng Service riêng biệt mà không cần gọi qua API.
- **Nhất quán (Error Handling)**: Hệ thống lỗi và response code được chuẩn hóa giúp Frontend dễ dàng tích hợp.
