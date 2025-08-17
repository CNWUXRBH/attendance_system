from pydantic import BaseModel
from typing import Optional
from datetime import date

class EmployeeBase(BaseModel):
    employee_no: str
    name: str
    gender: str
    phone: str
    email: str
    position: str
    hire_date: date
    is_admin: bool = False

class EmployeeCreate(EmployeeBase):
    password: str

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None

class Employee(EmployeeBase):
    employee_id: int

    class Config:
        from_attributes = True