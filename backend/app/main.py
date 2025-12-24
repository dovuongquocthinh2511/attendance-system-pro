from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import engine, SessionLocal, Base
from app.api.endpoints import auth, users, attendance, leave, profile
from app.core.security import hash_password
from app.models.user import User
from app.core.exceptions import BestmixException

def create_initial_data(db: Session):
    admin_user = db.query(User).filter(User.email == "admin@bestmix.vn").first()
    if not admin_user:
        print("--- KHỞI TẠO TÀI KHOẢN ADMIN MẶC ĐỊNH ---")
        user = User(
            email="admin@bestmix.vn",
            password_hash=hash_password("123456"), # Pass mặc định
            role="admin",
            odoo_employee_id=1, # Giả sử ID bên Odoo là 1
            is_active=True
        )
        db.add(user)
        db.commit()
        print("--- ĐÃ TẠO USER: admin@bestmix.vn / 123456 ---")

# Hàm lifespan: Chạy 1 lần khi Server khởi động (Startup)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Tạo bảng trong DB (Tương đương Odoo Upgrade module)
    Base.metadata.create_all(bind=engine)
    
    # 2. Tạo dữ liệu mẫu
    db = SessionLocal()
    try:
        create_initial_data(db)
    finally:
        db.close()
    
    yield
    # Phần code sau yield sẽ chạy khi Server tắt (Shutdown)

# --- KHỞI TẠO APP ---
app = FastAPI(
    title="Bestmix Pro HR API",
    version="1.0.0",
    lifespan=lifespan # Gắn hàm khởi tạo vào app
)

# --- CẤU HÌNH CORS ---
# Cho phép Frontend (React) gọi vào API này
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Môi trường Dev thì cho phép tất cả (*)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- EXCEPTION HANDLER ---
@app.exception_handler(BestmixException)
async def bestmix_exception_handler(request: Request, exc: BestmixException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "error_code": exc.error_code
        }
    )

# --- ĐĂNG KÝ ROUTER (Controller) ---
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
app.include_router(leave.router, prefix="/leave", tags=["leave"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])

# --- API TEST ---
@app.get("/")
def root():
    return {"message": "Bestmix Pro HR Backend is running!", "status": "ok"}