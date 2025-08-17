from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database.database import Base

class Warning(Base):
    __tablename__ = "warnings"

    warning_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    warning_type = Column(String(255), nullable=False)
    description = Column(String(1024))
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, server_default=func.now())