from pydantic import BaseModel
from datetime import time
from typing import Optional

class ShiftTypeBase(BaseModel):
    name: str
    start_time: time
    end_time: time
    description: Optional[str] = None

class ShiftTypeCreate(ShiftTypeBase):
    pass

class ShiftType(ShiftTypeBase):
    shift_type_id: int

    class Config:
        from_attributes = True