from pydantic import BaseModel
from datetime import date
from typing import Optional

class ScheduleBase(BaseModel):
    employee_id: int
    shift_type_id: int
    start_date: date
    end_date: date
    status: Optional[int] = 1

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    schedule_id: int

    class Config:
        from_attributes = True