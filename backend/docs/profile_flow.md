# Giải thích Luồng Hồ Sơ (Profile Flow)

Tài liệu này phân tích chi tiết mã nguồn của **`ProfileService`** (`backend/app/services/profile_service.py`), chuyên trách việc đồng bộ thông tin nhân viên 2 chiều giữa App và Odoo, cũng như tra cứu hợp đồng lao động.

## 1. Class `ProfileService`

Khác với Attendance hay Leave, service này chủ yếu làm nhiệm vụ **Read (Đọc)** thông tin từ Odoo về. Quyền **Write (Ghi)** bị giới hạn nghiêm ngặt để tránh nhân viên tự ý sửa dữ liệu nhạy cảm (như chức vụ, phòng ban, lương...).

---

---

## 1. Sơ đồ Tiếp nhận Yêu cầu (Request Flow)

Trước khi đi vào logic whitelist và đồng bộ, hãy xem luồng xử lý của một yêu cầu cập nhật hồ sơ.

### Sơ đồ Tổng quan

```mermaid
sequenceDiagram
    participant Client as Mobile App
    participant API as API Layer (/profile)
    participant Service as Profile Service
    participant Odoo as Odoo XML-RPC

    Note over Client, API: Header: Authorization: Bearer <token>

    Client->>API: PUT /profile (email, phone...)

    API->>API: Verify JWT & Get Current User

    API->>Service: update_profile(user_id, updates)

    Service->>Service: Filter Whitelist (Security)

    Service->>Odoo: write('hr.employee', updates)
    Odoo-->>Service: True
    Service-->>API: Return Success
    API-->>Client: 200 OK (JSON)
```

### Chi tiết các bước

#### Bước 1: Client gửi Request

- Mobile App gửi PUT request kèm `access_token`.
- Body chứa các field muốn sửa (ví dụ: `mobile_phone`, `birthday`...).

#### Bước 2: API Layer (`backend/app/api/endpoints/profile.py`)

- Endpoint `update_my_profile` tiếp nhận.

```python
@router.put("/", response_model=APIResponse[ActionResponse])
def update_my_profile(
    updates: ProfileUpdateRequest,
    current_user: User = Depends(deps.get_current_user)
):
    if not current_user.odoo_employee_id:
        raise HTTPException(status_code=400, detail="User not linked to Odoo Employee")

    update_data = updates.dict(exclude_unset=True)
    success = profile_service.update_profile(current_user.odoo_employee_id, update_data)

    if success:
         return APIResponse(data=ActionResponse(msg="Profile updated successfully", ...))
    return APIResponse(data=ActionResponse(msg="No changes made", ...))
```

---

## 2. Cập nhật Hồ sơ (`update_profile`)

Đây là tính năng quan trọng nhất cần kiểm soát bảo mật.

### Sơ đồ Logic

```mermaid
sequenceDiagram
    participant API as API update_profile
    participant Service as Profile Service
    participant Odoo as Odoo XML-RPC

    API->>Service: update_profile(data)

    Service->>Service: Filter Whitelist (Email, Phone...)

    alt No valid fields
        Service-->>API: Return False (Ignore)
    else Valid Data Exists
        Service->>Odoo: write([id], updates)
        Odoo-->>Service: Success
        Service-->>API: Return True
    end
```

### Chi tiết Code

(`backend/app/services/profile_service.py`)

#### Bước 1: Whitelist (Danh sách được phép)

```python
ALLOWED_FIELDS = {'mobile_phone', 'work_email', 'identification_id', 'birthday'}
```

- **Mục đích**: Chỉ cho phép nhân viên tự cập nhật thông tin liên lạc cá nhân.
- **Bảo mật**: Các field như `job_id` (Chức vụ), `department_id` (Phòng ban), `wage` (Lương) **tuyệt đối không có trong list này**. Dù hacker có gửi request chứa các field đó lên API, service cũng sẽ lọc bỏ ngay lập tức.

#### Bước 2: Lọc dữ liệu (Filtering)

```python
updates = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
if not updates:
    return False # Không có gì để update
```

- Dictionary comprehension này sẽ loại bỏ tất cả các key không nằm trong `ALLOWED_FIELDS`.

#### Bước 3: Ghi xuống Odoo

```python
odoo_client.execute_kw('hr.employee', 'write', [[odoo_employee_id], updates])
```

- Sử dụng hàm `write` của Odoo để cập nhật bản ghi Employee.

---

## 3. Xem Hợp đồng (`get_contract`)

Hàm này tìm hợp đồng lao động **đang hiệu lực** của nhân viên để hiển thị.

### Logic chọn Hợp đồng

Một nhân viên có thể có nhiều hợp đồng lịch sử (thử việc, chính thức lần 1, lần 2...). Hệ thống cần chọn ra cái mới nhất.

```python
domain = [
    ['employee_id', '=', odoo_employee_id],
    ['state', 'in', ['open', 'close', 'draft']]
]
# Sắp xếp: Mới nhất lên đầu
records = odoo_client.search_read(
    'hr.contract',
    domain,
    fields,
    order='date_start desc',
    limit=1
)
```

- **Điều kiện**:
  - `state` phải là `open` (Đang chạy), `draft` (Mới tạo), hoặc `close` (Vừa hết hạn/Đã đóng - để xem lại lịch sử gần nhất).
- **Sắp xếp**: `date_start desc` đảm bảo luôn lấy hợp đồng có ngày bắt đầu gần nhất.
- **Limit 1**: Chỉ lấy duy nhất 1 bản ghi.

---

## 4. Lấy thông tin cá nhân (`get_profile`)

Chỉ đơn giản là `search_read` từ model `hr.employee`.

```python
fields = [
    'id', 'name', 'job_title', 'department_id', 'work_email',
    'mobile_phone', 'work_phone', 'work_location_id',
    'parent_id', 'birthday', 'identification_id'
]
```

- Đây là danh sách các field sẽ hiển thị trên màn hình "Hồ sơ của tôi" trên App.
