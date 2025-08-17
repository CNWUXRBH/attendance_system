from pydantic import BaseModel
from typing import Optional
from datetime import date

class HolidayBase(BaseModel):
    name: str
    date: date
    type: str
    description: Optional[str] = None

class HolidayCreate(HolidayBase):
    pass

class Holiday(HolidayBase):
    holiday_id: int

    class Config:
        from_attributes = True