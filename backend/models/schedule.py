from sqlalchemy import Column, Integer, String, Date, ForeignKey, DATETIME, func
from sqlalchemy.orm import relationship
from database.database import Base

class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    shift_type_id = Column(Integer, ForeignKey("shift_types.shift_type_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Integer, default=1)
    created_at = Column(DATETIME, server_default=func.now())
    updated_at = Column(DATETIME, server_default=func.now(), onupdate=func.now())

    employee = relationship("Employee")
    shift_type = relationship("ShiftType")