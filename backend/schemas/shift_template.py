from pydantic import BaseModel, validator
from datetime import time, date
from typing import List, Union

class ShiftTemplateBase(BaseModel):
    name: str
    start_time: time
    end_time: time

class ShiftTemplateCreate(ShiftTemplateBase):
    pass

class ShiftTemplate(ShiftTemplateBase):
    id: int

    class Config:
        from_attributes = True

class ShiftTemplateApply(BaseModel):
    template_id: int
    employee_ids: List[int]
    start_date: Union[date, str]
    end_date: Union[date, str]
    
    @validator('start_date', 'end_date', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            return date.fromisoformat(v)
        return v