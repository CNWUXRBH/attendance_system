from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class AttendanceRecordBase(BaseModel):
    employee_id: int
    clock_in_time: Optional[datetime] = None
    clock_out_time: Optional[datetime] = None
    clock_type: Optional[str] = None
    device_id: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = "正常"
    process_status: Optional[str] = "unprocessed"
    remarks: Optional[str] = None

class AttendanceRecordCreate(AttendanceRecordBase):
    pass

class AttendanceRecordUpdate(BaseModel):
    employee_id: Optional[int] = None
    date: Optional[date] = None
    clock_in_time: Optional[datetime] = None
    clock_out_time: Optional[datetime] = None
    clock_type: Optional[str] = None
    device_id: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    process_status: Optional[str] = None
    remarks: Optional[str] = None

class AttendanceRecord(AttendanceRecordBase):
    record_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AttendanceRecordResponse(BaseModel):
    record_id: int
    date: str
    name: str
    department: str
    checkIn: Optional[str] = None
    checkOut: Optional[str] = None
    status: str
    employee_id: int
    clock_type: Optional[str] = None
    device_id: Optional[str] = None
    location: Optional[str] = None
    process_status: Optional[str] = None
    remarks: Optional[str] = None
    workHours: Optional[str] = None
    overtimeHours: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True