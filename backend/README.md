# Bestmix Pro - Backend

## 📖 Giới thiệu

**Bestmix Pro** là hệ thống quản lý nhân sự nội bộ (HRM) được thiết kế hiện đại với kiến trúc 3-tier, giúp tối ưu hóa quy trình chấm công, nghỉ phép và quản lý hồ sơ nhân viên.

Dự án đóng vai trò là cầu nối thông minh gữa người dùng và hệ thống Odoo ERP, giúp nhân viên thao tác nhanh chóng trên giao diện Mobile-first PWA mà không cần truy cập trực tiếp vào Odoo.

### 🚀 Tính năng chính

- **Chấm công online (Attendance)**: Check-in/Check-out dễ dàng, tự động đồng bộ với Odoo.
- **Quản lý nghỉ phép (Leave)**: Tạo đơn, duyệt đơn và theo dõi phép tồn theo thời gian thực.
- **Hồ sơ nhân viên (Profile)**: Xem và cập nhật thông tin cá nhân, hợp đồng lao động.
- **Tiết kiệm License**: Backend hoạt động như một Proxy Server, giảm thiểu số lượng user Odoo cần thiết.

### 🛠 Công nghệ sử dụng

- **Frontend**: ReactJS, Vite PWA (Mobile-first).
- **Backend**: FastAPI (Python), PostgreSQL (Lưu trữ user/auth local).
- **Data Layer**: Odoo 18.0 (Hệ thống Core HR).

---

## ⚙️ Hướng dẫn Cài đặt & Khởi chạy

Có thể chạy dự án bằng **Docker** hoặc thiết lập môi trường thủ công.

### Cách 1: Chạy bằng Docker

Phương pháp này giúp đóng gói toàn bộ môi trường backend và database, tránh xung đột thư viện.

**Yêu cầu**: Cài đặt [Docker Desktop](https://www.docker.com/products/docker-desktop).

**Bước 1: Cấu hình môi trường**
Tại thư mục `backend` (thư mục hiện tại), tạo file `.env`. Có thể copy từ `.env` mẫu nếu có, hoặc sử dụng cấu hình cơ bản sau:

```env
# backend/.env
DATABASE_URL=postgresql://bestmix_user:bestmix_pass@db/bestmix_auth_db
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=60
ODOO_URL=http://host.docker.internal:8069
ODOO_DB=your_odoo_db
ODOO_USER=your_odoo_admin_user
ODOO_PASSWORD=your_odoo_admin_password
```

> **Lưu ý**: `ODOO_URL` được set là `host.docker.internal` để Docker container có thể giao tiếp với Odoo chạy trên máy host (localhost).

**Bước 2: Khởi chạy**
Quay trở lại thư mục gốc của dự án (`cd ..`), chạy lệnh:

```bash
docker-compose up -d --build
```

Lệnh này sẽ:

1.  Khởi tạo PostgreSQL database.
2.  Build và chạy Backend FastAPI.

**Bước 3: Truy cập**

- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

### Cách 2: Chạy Thủ công

Nếu muốn debug hoặc phát triển, hãy cài đặt môi trường ảo (Virtual Environment).

#### 1. Khởi chạy Backend

**Yêu cầu**: Python 3.10+
**Vị trí**: Thực hiện tại thư mục `backend`.

**Bước 1: Tạo môi trường ảo (venv)**

```bash
python -m venv venv
```

**Bước 2: Kích hoạt môi trường**

- **Windows**:
  ```powershell
  .\venv\Scripts\activate
  ```
- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

**Bước 3: Cài đặt thư viện**

```bash
pip install -r requirements.txt
```

**Bước 4: Cấu hình môi trường**
Tạo file `.env` tại thư mục này (tương tự như phần Docker), nhưng thay đổi `DATABASE_URL` và `ODOO_URL` nếu cần:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
ODOO_URL=http://localhost:8069
```

_Lưu ý: Bạn cần tự cài đặt và chạy PostgreSQL nếu chạy thủ công._

**Bước 5: Chạy Server**

```bash
uvicorn app.main:app --reload
```

#### 2. Khởi chạy Frontend

Để chạy Frontend, vui lòng tham khảo hướng dẫn trong thư mục `../frontend` hoặc:

**Yêu cầu**: Node.js 16+

**Bước 1: Di chuyển sang thư mục Frontend**

```bash
cd ../frontend
```

**Bước 2: Cài đặt thư viện**

```bash
npm install
```

**Bước 3: Chạy Development Server**

```bash
npm run dev
```

Truy cập Frontend tại: `http://localhost:5173` (hoặc port hiển thị trên terminal).

---

## 📂 Cấu trúc Dự án

```
bestmix-pro/
├── backend/            # FastAPI Project
│   ├── app/            # Source code (API, Services, Models)
│   ├── Dockerfile      # Cấu hình build Docker cho backend
│   └── requirements.txt
├── frontend/           # ReactJS Project
├── docker-compose.yml  # Cấu hình Docker cho toàn bộ hệ thống
└── .kiro/              # Tài liệu thiết kế & Specs
```
