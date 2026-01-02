# Giải thích Luồng Nghỉ phép (Leave Flow)

Tài liệu này mô tả quy trình tạo đơn, duyệt đơn và quản lý phép trong hệ thống **Bestmix Pro**.

## Vòng đời Đơn nghỉ phép (State Lifecycle)

Đơn nghỉ phép trong Odoo (`hr.leave`) trải qua các trạng thái sau:

1.  **Draft** (`draft`): Mới tạo, chưa gửi đi.
2.  **Confirmed** (`confirm`): Đã gửi, chờ duyệt (Pending).
3.  **Validated** (`validate`): Đã được duyệt (Approved).
4.  **Refused** (`refuse`): Bị từ chối (Rejected).

---

## 1. Tạo & Gửi Đơn

### Sơ đồ luồng dữ liệu

```mermaid
graph TD
    User[Mobile App] -->|1. Create Draft| Service[Leave Service]
    Service -->|2. Validate Dates| Logic{Valid Dates?}
    Logic -->|No| Error[Error Response]
    Logic -->|Yes| Odoo1[Odoo: Create]

    User -->|3. Confirm (Send)| Service
    Service -->|4. Check Overlap| Check1{Overlap?}
    Check1 -->|Yes| Error
    Check1 -->|No| Check2{Balance Enough?}
    Check2 -->|No| Error
    Check2 -->|Yes| Odoo2[Odoo: Action Confirm]
```

### Chi tiết xử lý (`LeaveService`)

#### A. Tạo Nháp (`create_request`)

1.  **Validate Ngày**: Đảm bảo `date_to >= date_from` và không chọn ngày trong quá khứ.
2.  **Tạo Record**: Gọi Odoo `create` trên model `hr.leave`. Trạng thái mặc định là `draft`.

#### B. Gửi Đơn (`confirm_request`)

Hàm này chuyển trạng thái từ `draft` -> `confirm`. Trước khi chuyển, hệ thống thực hiện các kiểm tra quan trọng:

1.  **Check Overlap (Trùng lịch)**:
    - Hàm `_check_overlap`: Query Odoo xem có đơn nào đã duyệt (`validate`) hoặc đang chờ (`confirm`) nằm trong khoảng thời gian này không.
    - Nếu có -> Chặn ngay lập tức.
2.  **Check Balance (Số dư phép)**:

    - Hàm `_check_balance`: Gọi Odoo (hoặc tự tính) để kiểm tra số ngày phép còn lại (`remaining_leaves`) của loại nghỉ phép đó (`holiday_status_id`).
    - Nếu số dư < số ngày xin nghỉ -> Báo lỗi.

3.  **Action Confirm**:
    - Nếu tất cả hợp lệ, gọi method `action_confirm` của Odoo model để chuyển trạng thái.

---

## 2. Quản lý Phép (Duyệt/Từ chối)

Các hành động này dành cho Manager/Admin:

- **Approve**: Gọi method `action_validate` trên Odoo. Đơn chuyển sang trạng thái `validate`. Ngày phép sẽ chính thức bị trừ.
- **Reject**: Gọi method `action_refuse`. Đơn chuyển sang trạng thái `refuse`. Ngày phép (nếu đã trừ tạm) sẽ được hoàn lại.

---

## 3. Tra cứu Số dư (`get_balance`)

Đây là chức năng phức tạp nhất do cần tổng hợp dữ liệu từ Odoo.

### Logic tính toán

Do API Odoo có thể không expose trực tiếp phương thức lấy số dư dễ dàng, Service thực hiện tính toán thủ công (`LeaveService.get_balance`):

1.  **Lấy Phân bổ (Allocation)**:
    - Query `hr.leave.allocation`: Lấy tổng số ngày phép được cấp cho nhân viên theo từng loại (`holiday_status_id`).
2.  **Lấy Đã dùng (Taken)**:
    - Query `hr.leave`: Lấy tổng số ngày phép của các đơn đã duyệt (`validate`) hoặc đang chờ (`confirm`).
3.  **Tính toán**:
    - `Remaining` (Còn lại) = `Allocated` (Được cấp) - `Taken` (Đã dùng).
4.  **Kết quả**:
    - Trả về danh sách các loại phép kèm theo số liệu: _Tổng, Đã dùng, Còn lại_.
