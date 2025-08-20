from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "your-secret-key-change-in-production"
    # Email Configuration
    EMAIL_SENDER: str
    EMAIL_DATA_RECIPIENT: str
    EMAIL_ERROR_RECIPIENT: str
    EMAIL_SMTP_SERVER: str
    EMAIL_SMTP_PORT: int
    EMAIL_DATA_SUBJECT: str
    EMAIL_ERROR_SUBJECT: str
    
    # MSSQL数据库配置
    MSSQL_SERVER: str = "localhost"
    MSSQL_DATABASE: str = "AttendanceDB"
    MSSQL_USERNAME: str = "sa"
    MSSQL_PASSWORD: str = "password"
    MSSQL_DRIVER: str = "ODBC Driver 17 for SQL Server"
    
    # 环境配置
    ENVIRONMENT: Optional[str] = "production"
    DEBUG: Optional[bool] = False
    SYNC_INTERVAL_MINUTES: Optional[int] = None

    class Config:
        env_file = ".env"

settings = Settings()