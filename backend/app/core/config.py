import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Config
    PROJECT_NAME: str = "Bestmix Pro HR"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "chuoi_bi_mat")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://bestmix_user:bestmix_pass@db/bestmix_auth_db")

    # Odoo Config    
    ODOO_URL: str = os.getenv("ODOO_URL", "http://localhost:8069")
    ODOO_DB: str = os.getenv("ODOO_DB", "bm_db")
    ODOO_USERNAME: str = os.getenv("ODOO_USERNAME", "admin")
    ODOO_PASSWORD: str = os.getenv("ODOO_PASSWORD", "odoo")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
