from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "your-secret-key-change-in-production"
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_sender_email: str
    
    # MSSQL数据库配置
    MSSQL_SERVER: str = "localhost"
    MSSQL_DATABASE: str = "AttendanceDB"
    MSSQL_USERNAME: str = "sa"
    MSSQL_PASSWORD: str = "password"
    MSSQL_DRIVER: str = "ODBC Driver 17 for SQL Server"

    class Config:
        env_file = ".env"

settings = Settings()