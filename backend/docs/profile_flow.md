# Giải thích Luồng Hồ sơ Nhân viên (Profile Flow)

Tài liệu này mô tả cách Backend tương tác với Odoo để quản lý thông tin nhân viên và hợp đồng lao động.

## 1. Xem Hồ sơ (`get_profile`)

### Quy trình

Backend đóng vai trò query trực tiếp thông tin từ model `hr.employee` của Odoo.

- **Model**: `hr.employee`
- **Input**: `odoo_employee_id` (Lưu trong User Access Token).
- **Output fields**:
  - Cơ bản: `name`, `birthday`, `identification_id` (CCCD/CMND).
  - Công việc: `job_title`, `department_id`, `parent_id` (Manager).
  - Liên hệ: `work_email`, `work_phone`, `mobile_phone`.

### Xử lý logic

- Hệ thống dùng hàm `search_read` với domain `[['id', '=', odoo_employee_id]]`.
- Dữ liệu trả về là raw data từ Odoo, Backend sẽ chuyển tiếp (proxy) về cho Mobile App hiển thị.

---

## 2. Cập nhật Hồ sơ (`update_profile`)

Để đảm bảo an toàn dữ liệu, hệ thống **không cho phép** cập nhật tất cả các trường.

### whitelist Fields (Danh sách cho phép)

Chỉ có các trường sau được phép sửa từ Mobile App:

1.  `mobile_phone`: Số điện thoại di động.
2.  `work_email`: Email công việc (nếu chính sách cho phép).
3.  `identification_id`: Số giấy tờ tùy thân.
4.  `birthday`: Ngày sinh.

### Logic cập nhật

1.  **Lọc dữ liệu**: Service sẽ nhận `dict` dữ liệu từ Client, sau đó lọc bỏ tất cả các key không nằm trong whitelist.
2.  **Gửi Odoo**:
    - Nếu không còn trường nào hợp lệ -> Bỏ qua.
    - Nếu có -> Gọi `odoo_client.execute_kw('hr.employee', 'write', [[id], updates])`.

---

## 3. Xem Hợp đồng (`get_contract`)

Thông tin hợp đồng thường nhạy cảm và quan trọng, được lưu ở model riêng biệt.

- **Model**: `hr.contract`
- **Logic tìm kiếm**:

  - Tìm hợp đồng thuộc về `employee_id`.
  - Trạng thái phải là "Đang hiệu lực": `['state', 'in', ['open', 'close', 'draft']]`.
  - Sắp xếp: `date_start desc` (Lấy hợp đồng mới nhất).
  - Limit: 1.

- **Thông tin trả về**:
  - `name`: Tên hợp đồng.
  - `wage`: Mức lương (có thể ẩn tùy user role).
  - `date_start`, `date_end`: Thời hạn hợp đồng.
  - `job_id`: Vị trí công việc trong hợp đồng.
