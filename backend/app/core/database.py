import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# Lấy URL từ Settings
DATABASE_URL = settings.DATABASE_URL

# --- THÊM ĐOẠN RETRY NÀY ---
def get_engine():
    retries = 5
    while retries > 0:
        try:
            # Thử kết nối
            engine = create_engine(DATABASE_URL)
            connection = engine.connect()
            connection.close()
            print("--- KẾT NỐI DATABASE THÀNH CÔNG! ---")
            return engine
        except Exception as e:
            print(f"--- Database chưa sẵn sàng, thử lại sau 2s... (Lỗi: {e}) ---")
            time.sleep(2)
            retries -= 1
    raise Exception("Không thể kết nối Database sau 5 lần thử!")

# Khởi tạo engine với cơ chế retry
engine = get_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()