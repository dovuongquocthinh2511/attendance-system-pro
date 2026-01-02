# Giải thích Luồng Người dùng (User Flow)

Tài liệu này phân tích chi tiết mã nguồn của **`UserService`** (`backend/app/services/user_service.py`). Khác với 3 service còn lại, service này hoạt động chủ yếu trên **Local Database (PostgreSQL)** để quản lý tài khoản đăng nhập, nhưng có cơ chế **Auto-link** đặc biệt để kết nối với Odoo.

## 1. Cơ chế Tự động Liên kết (Auto-linking)

Hệ thống Bestmix Pro cho phép tạo user local trước, sau đó tự động tìm và map với nhân viên trong Odoo dựa trên Email hoặc SĐT.

### Sơ đồ Logic (Tạo User)

```mermaid
flowchart TD
    A[API: create_user(email, phone)] --> B{Email/Phone đã tồn tại Local?}
    B -- Có --> C[Raise Error 'Already registered']
    B -- Chưa --> D[Hash Password]
    D --> E{Có Odoo ID chưa?}
    E -- Chưa --> F[Gọi EmployeeService.find_by_email_or_phone()]
    F --> G[Tìm thấy Employee ID=99]
    G --> H[Gán Odoo ID = 99 vào User]
    E -- Có rồi --> H
    H --> I[Lưu vào Local DB]
    I --> J[Return User]
```

### Chi tiết Code

(`backend/app/services/user_service.py`)

#### A. Hàm `create_user`

1.  **Kiểm tra trùng lặp Local**:

    - Query DB local xem `email` hoặc `phone` đã được tài khoản nào dùng chưa. Nếu có -> Báo lỗi ngay.

2.  **Logic Auto-link**:

    ```python
    odoo_employee_id = user_in.odoo_employee_id
    if not odoo_employee_id:
        # Gọi sang EmployeeService để tìm trong Odoo
        odoo_employee_id = employee_service.find_by_email_or_phone(
            user_in.email, user_in.phone
        )
    ```

    - Nếu lúc tạo user, admin không nhập ID Odoo, hệ thống sẽ tự đi tìm xem có nhân viên nào trong Odoo dùng chung Email/SĐT đó không.
    - **Lợi ích**: Giúp đồng bộ user cũ vào hệ thống mới mà không cần mapping thủ công từng người.

3.  **Lưu User**:
    - Mật khẩu được mã hóa bằng `bcrypt` trước khi lưu (`user_in.password_hash`).

#### B. Hàm `update_user` (Cập nhật User)

Logic tương tự cũng được áp dụng khi cập nhật thông tin:

```python
if 'odoo_employee_id' not in update_data:
    # Nếu user đổi Email hoặc Phone
    if new_email is not None or new_phone is not None:
        # Hệ thống tự chạy lại logic tìm kiếm để update liên kết
        found_id = employee_service.find_by_email_or_phone(final_email, final_phone)
        update_data['odoo_employee_id'] = found_id
```

- **Ví dụ**: User A ban đầu dùng email cá nhân (chưa link được Odoo). Sau đó User A đổi sang email công ty. Hệ thống sẽ ngay lập tức tìm thấy nhân viên Odoo tương ứng và tự động cập nhật `odoo_employee_id` cho User A.

---

## 2. Quản lý Đội nhóm (`get_team`)

Hàm này giúp Manager xem danh sách nhân viên cấp dưới trực tiếp.

```python
def get_team(self, manager_employee_id: int) -> List[Dict]:
    domain = [['parent_id', '=', manager_employee_id]]
    return odoo_client.search_read('hr.employee', domain, ...)
```

- **Logic Odoo**: Trong Odoo, mỗi nhân viên có field `parent_id` trỏ về người quản lý của mình.
- Backend query tất cả nhân viên có `parent_id` bằng ID của user hiện tại.

---

## 3. Các hàm CRUD cơ bản

- **`get_users`**: Lấy danh sách user local (có phân trang `skip`, `limit`).
- **`get_user_by_id`**: Lấy chi tiết user theo ID.
- **`delete_user`**: Xóa user khỏi DB Local (Không xóa nhân viên bên Odoo).
