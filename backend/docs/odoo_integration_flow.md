# Tích hợp Odoo qua XML-RPC

Tài liệu này giải thích cơ chế kỹ thuật mà Backend FastAPI sử dụng để giao tiếp với Odoo ERP. Backend sử dụng giao thức **XML-RPC** (giao thức chuẩn được Odoo hỗ trợ) để thực hiện các thao tác đọc/ghi dữ liệu.

## 1. Cấu hình Kết nối

Để kết nối được, Backend cần thông tin tài khoản của một **System User** (thường là Admin hoặc một user service account có đủ quyền).

### Biến môi trường

Cấu hình trong file `.env`:

- `ODOO_URL`: Địa chỉ server Odoo (vd: `http://localhost:8069`).
- `ODOO_DB`: Tên database trong Odoo.
- `ODOO_USERNAME`: Email/Username đăng nhập.
- `ODOO_PASSWORD`: Password (hoặc API Key - khuyên dùng).

---

## 2. OdooClient Wrapper

Dự án sử dụng lớp `OdooClient` (`backend/app/services/odoo_client.py`) để bao đóng các phức tạp của thư viện `xmlrpc.client`.

### Quy trình Authenticate

Mỗi khi khởi động hoặc cần thực hiện request, Client sẽ thực hiện:

1.  **Kết nối Common Endpoint**: `/xmlrpc/2/common`.
2.  **Gọi hàm authenticate**:
    ```python
    uid = common.authenticate(db, username, password, {})
    ```
    - Kết quả trả về là `user_id` (UID) (số nguyên).
    - UID này sẽ được dùng cho mọi request dữ liệu sau đó.

### Quy trình Gọi Method (`execute_kw`)

Đây là hàm quan trọng nhất để tương tác với Odoo Models. Endpoint sử dụng là `/xmlrpc/2/object`.

**Cú pháp chuẩn**:

```python
models.execute_kw(
    db, uid, password,
    <Model Name>, <Method Name>,
    <List of Arguments>,
    <Keyword Arguments>
)
```

**Các Method phổ biến được sử dụng**:

| Method           | Ý nghĩa                 | Ví dụ sử dụng                                   |
| :--------------- | :---------------------- | :---------------------------------------------- |
| `search_read`    | Tìm kiếm và lấy dữ liệu | Lấy danh sách nhân viên, lịch sử chấm công      |
| `create`         | Tạo bản ghi mới         | Tạo đơn nghỉ phép, created check-in             |
| `write`          | Cập nhật bản ghi        | Check-out (update giờ ra), duyệt đơn            |
| `unlink`         | Xóa bản ghi             | (Ít dùng trong dự án này)                       |
| _Custom methods_ | Các hàm custom của Odoo | `action_confirm`, `action_validate` (Duyệt đơn) |

---

## 3. Xử lý Lỗi (Error Handling)

Việc giao tiếp qua mạng với hệ thống bên ngoài luôn tiềm ẩn rủi ro. `OdooClient` xử lý các lỗi sau:

- **OdooConnectionError**: Không thể kết nối tới server Odoo (Network down, sai URL).
- **AuthenticationError**: Sai user/pass hoặc DB không tồn tại.
- **OdooAPIError**: Lỗi nghiệp vụ từ phía Odoo trả về (vd: Vi phạm ràng buộc dữ liệu, thiếu quyền truy cập).

Tất cả các exception từ thư viện `xmlrpc` đều được catch và wrap lại thành các Custom Exception của dự án để API trả về mã lỗi HTTP phù hợp (thường là 502 Bad Gateway hoặc 503 Service Unavailable).
