from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME, func, Boolean
from sqlalchemy.orm import relationship
from database.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DATETIME, server_default=func.now())

    employee = relationship("Employee")