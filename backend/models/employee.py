from sqlalchemy import (Column, Integer, String, DATETIME, func, Date, Boolean)
from sqlalchemy.orm import relationship
from database.database import Base

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_no = Column(String(20), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(255), nullable=True)
    position = Column(String(50))
    hire_date = Column(Date)
    contract_end_date = Column(Date)
    status = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DATETIME, default=func.now())
    updated_at = Column(DATETIME, default=func.now(), onupdate=func.now())