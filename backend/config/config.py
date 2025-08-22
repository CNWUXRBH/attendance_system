from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
import os

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = Field(..., description="MySQL数据库连接URL")
    
    # JWT配置
    SECRET_KEY: str = Field(..., description="JWT签名密钥")
    ALGORITHM: str = Field(default="HS256", description="JWT算法")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="访问令牌过期时间(分钟)")
    
    # 邮件配置 - 设为可选
    EMAIL_SENDER: Optional[str] = Field(default=None, description="发件人邮箱")
    EMAIL_DATA_RECIPIENT: Optional[str] = Field(default=None, description="数据接收邮箱")
    EMAIL_ERROR_RECIPIENT: Optional[str] = Field(default=None, description="错误接收邮箱")
    EMAIL_SMTP_SERVER: Optional[str] = Field(default=None, description="SMTP服务器地址")
    EMAIL_SMTP_PORT: Optional[int] = Field(default=None, description="SMTP服务器端口")
    EMAIL_DATA_SUBJECT: Optional[str] = Field(default=None, description="数据邮件主题")
    EMAIL_ERROR_SUBJECT: Optional[str] = Field(default=None, description="错误邮件主题")
    
    # MSSQL数据库配置
    MSSQL_SERVER: str = Field(default="localhost", description="MSSQL服务器地址")
    MSSQL_DATABASE: str = Field(default="AttendanceDB", description="MSSQL数据库名")
    MSSQL_USERNAME: str = Field(default="sa", description="MSSQL用户名")
    MSSQL_PASSWORD: Optional[str] = Field(default=None, description="MSSQL密码")
    MSSQL_DRIVER: str = Field(default="ODBC Driver 17 for SQL Server", description="MSSQL驱动")
    
    # 环境配置
    ENVIRONMENT: str = Field(default="production", description="运行环境")
    DEBUG: bool = Field(default=False, description="调试模式")
    SYNC_INTERVAL_MINUTES: Optional[int] = Field(default=5, description="同步间隔(分钟)")
    
    # 安全配置
    CORS_ORIGINS: list = Field(default=["http://localhost:3000"], description="允许的CORS源")
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, description="每分钟请求限制")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE: Optional[str] = Field(default=None, description="日志文件路径")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        if not v:
            raise ValueError('DATABASE_URL is required')
        return v
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    @validator('EMAIL_SMTP_PORT')
    def validate_smtp_port(cls, v):
        if v is not None and not (1 <= v <= 65535):
            raise ValueError('EMAIL_SMTP_PORT must be between 1 and 65535')
        return v
    
    @validator('SYNC_INTERVAL_MINUTES')
    def validate_sync_interval(cls, v):
        if v is not None and v < 1:
            raise ValueError('SYNC_INTERVAL_MINUTES must be at least 1')
        return v
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def email_enabled(self) -> bool:
        """检查邮件功能是否启用"""
        return all([
            self.EMAIL_SENDER,
            self.EMAIL_SMTP_SERVER,
            self.EMAIL_SMTP_PORT
        ])
    
    @property
    def mssql_enabled(self) -> bool:
        """检查MSSQL功能是否启用"""
        return all([
            self.MSSQL_SERVER,
            self.MSSQL_DATABASE,
            self.MSSQL_USERNAME,
            self.MSSQL_PASSWORD
        ])

# 创建全局设置实例
try:
    settings = Settings()
    print("配置加载成功!")
    print(f"环境: {settings.ENVIRONMENT}")
    print(f"数据库: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else '配置中'}")
    print(f"邮件功能: {'启用' if settings.email_enabled else '禁用'}")
    print(f"MSSQL功能: {'启用' if settings.mssql_enabled else '禁用'}")
except Exception as e:
    print(f"配置加载失败: {e}")
    print("请检查环境变量配置")
    exit(1)