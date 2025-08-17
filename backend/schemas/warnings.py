from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WarningBase(BaseModel):
    employee_id: int
    warning_type: str
    description: Optional[str] = None
    status: str = 'pending'

class WarningCreate(WarningBase):
    pass

class Warning(WarningBase):
    warning_id: int
    created_at: datetime

    class Config:
        from_attributes = True