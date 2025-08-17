from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME, func
from sqlalchemy.orm import relationship
from database.database import Base

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    record_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    clock_in_time = Column(DATETIME)
    clock_out_time = Column(DATETIME)
    clock_type = Column(String(50))
    device_id = Column(String(255))
    location = Column(String(255))
    status = Column(String(50))
    process_status = Column(String(50), default='unprocessed')  # 异常处理状态: unprocessed, processing, processed
    remarks = Column(String(500))  # 备注信息
    created_at = Column(DATETIME, server_default=func.now())
    updated_at = Column(DATETIME, server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee")