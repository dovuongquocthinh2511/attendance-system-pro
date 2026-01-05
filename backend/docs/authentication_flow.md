# Giải thích Luồng Xác thực (Authentication Flow)

Tài liệu này giải thích chi tiết cơ chế đăng nhập của hệ thống **Bestmix Pro**, đi từ lúc ứng dụng Mobile gửi yêu cầu cho đến khi nhận được kết quả.

## Sơ đồ Tổng quan

```mermaid
sequenceDiagram
    participant Client as Mobile App (Client)
    participant API as API Layer (Endpoint)
    participant Service as Auth Service
    participant DB as Local Database (PostgreSQL)
    participant Security as Security Utils

    Client->>API: 1. POST /auth/login (username, password)
    API->>Service: 2. auth_service.login(db, username, password)
    Service->>DB: 3. Query User by email/phone
    DB-->>Service: User Record (có password_hash)
    Service->>Security: 4. verify_password(input_pass, hash)
    Security-->>Service: True/False

    alt Login False
        Service-->>API: Exception 401 Unauthorized
        API-->>Client: Error Message
    else Login True
        Service->>Security: 5. create_access_token(data)
        Security-->>Service: JWT Token string
        Service-->>API: TokenResponse (access_token, role...)
        API-->>Client: 6. APIResponse (Success + Data)
    end
```

## Chi tiết từng bước xử lý

### 1. Client Gửi Yêu cầu (`LoginRequest`)

- **Hành động**: Người dùng nhập Email/SĐT và Mật khẩu trên app, nhấn "Đăng nhập".
- **Dữ liệu gửi đi**: JSON body chứa `username` (là email hoặc sđt) và `password`.
- **Đích đến**: Endpoint `/auth/login` trên Backend.

### 2. API Layer - Tiếp nhận (`backend/app/api/endpoints/auth.py`)

Khi request đến, hàm `login` sẽ được kích hoạt:

```python
@router.post("/login", ...)
def login(user_in: LoginRequest, db: Session = Depends(deps.get_db)):
    token = auth_service.login(db=db, username=user_in.username, password=user_in.password)
    return APIResponse(data=token)
```

- **Nhiệm vụ**:
  - Validate dữ liệu đầu vào (nhờ `LoginRequest` schema).
  - Gọi xuống tầng Service để xử lý logic chính: `auth_service.login()`.
  - Nhận kết quả và đóng gói vào `APIResponse` chuẩn.

### 3. Service Layer - Xử lý nghiệp vụ (`backend/app/services/auth_service.py`)

Đây là "bộ não" xử lý logic. Hàm `login` thực hiện 2 việc chính: Xác thực và Tạo Token.

#### A. Hàm `authenticate` - Kiểm tra thông tin

```python
def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
    # 1. Tìm user trong DB theo email HOẶC phone
    user = db.query(User).filter(
        or_(User.email == username, User.phone == username)
    ).first()

    if not user:
        return None  # Không tìm thấy user

    # 2. Kiểm tra mật khẩu
    if not security.verify_password(password, user.password_hash):
        return None  # Mật khẩu sai

    return user  # Hợp lệ
```

- **Giải thích**: Hệ thống tìm user trong Database. Nếu có, nó lấy `password_hash` (mật khẩu đã mã hóa) từ DB ra và so sánh với mật khẩu người dùng nhập vào (bằng hàm `verify_password`).

#### B. Hàm `login` - Điều phối chung

```python
def login(self, db: Session, username: str, password: str) -> TokenResponse:
    # Gọi hàm authenticate ở trên
    user = self.authenticate(db, username, password)
    if not user:
        # Nếu sai thì báo lỗi ngay lại cho API
        raise HTTPException(status_code=401, detail="Incorrect email/phone or password")

    # Nếu đúng, tạo Token
    access_token = security.create_access_token(
        data={"sub": str(user.id), "role": user.role, "odoo_employee_id": user.odoo_employee_id}
    )

    # Trả về kết quả
    return {
        "access_token": access_token,
        "token_type": "bearer",
        ...
    }
```

### 4. Security Layer - Tiện ích bảo mật (`backend/app/core/security.py`)

Các hàm tiện ích được Service gọi đến:

- **`verify_password`**: Dùng thư viện `passlib[bcrypt]` để so sánh mật khẩu.

  ```python
  def verify_password(plain_password: str, hashed_password: str) -> bool:
      return pwd_context.verify(plain_password, hashed_password)
  ```

- **`create_access_token`**: Tạo chuỗi JWT với thời gian hết hạn (`exp`) và secret key.

  ```python
  def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
      to_encode = data.copy()
      if expires_delta:
          expire = datetime.utcnow() + expires_delta
      else:
          expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

      to_encode.update({"exp": expire})
      encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
      return encoded_jwt
  ```

  - **Payload**: Chứa `sub` (user id), `role`, `odoo_employee_id`.
  - **Signature**: Ký bằng `SECRET_KEY` + `ALGORITHM` (HS256).

### 5. Phản hồi về Client

Cuối cùng, API trả về JSON cho Mobile App:

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "role": "employee",
    "odoo_employee_id": 123
  },
  "error": null
}
```

Mobile App sẽ lưu `access_token` này và đính kèm vào header của các request sau (`Authorization: Bearer <token>`) để chứng minh danh tính.

---

### 6. Luồng Đăng Xuất (Logout Flow)

Hệ thống sử dụng cơ chế **Blacklist** để vô hiệu hóa Token.

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant DB as DB (TokenBlacklist)

    Client->>API: POST /auth/logout (Header: Bearer Token)
    API->>Service: auth_service.logout(db, token)
    Service->>DB: Check if exists in Blacklist?
    alt Not Blacklisted
        Service->>DB: INSERT INTO token_blacklist (token)
        DB-->>Service: Commit Success
    end
    Service-->>API: Success
    API-->>Client: "Logged out successfully"
```

- **Logic**: Khi Logout, server không xóa Token (do JWT stateless) mà lưu nó vào bảng đen (`token_blacklist`).
- **Hệ quả**: Ở các request sau, `deps.get_current_user` sẽ kiểm tra bảng này. Nếu Token dính blacklist -> Trả về lỗi `401 Unauthorized`.

---

### 7. Luồng Làm mới Token (Refresh Token Flow)

Hệ thống sử dụng chiến lược **Token Rotation** (Dùng token cũ để đổi token mới).

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant Security

    Note over Client: Token sắp hết hạn (ví dụ còn 5 phút)
    Client->>API: POST /auth/refresh (Header: Bearer OldToken)
    API->>Service: auth_service.refresh_token(current_user)
    Service->>Security: create_access_token(user_data)
    Security-->>Service: New JWT Strings
    Service-->>API: TokenResponse (New Token, Reset 60m)
    API-->>Client: { "access_token": "NewToken...", ... }
```

- **Điều kiện**: Client phải gửi request này **TRƯỚC** khi Token cũ hết hạn hoàn toàn.
- **Tác dụng**: Cấp lại `access_token` mới với thời hạn (expiry) được reset lại từ đầu (mặc định 60 phút), giúp user duy trì phiên làm việc liên tục mà không cần đăng nhập lại password.
