from pydantic import BaseModel
from typing import Optional
from datetime import time

class OvertimeRuleBase(BaseModel):
    name: str
    rate: float
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class OvertimeRuleCreate(OvertimeRuleBase):
    pass

class OvertimeRule(OvertimeRuleBase):
    rule_id: int

    class Config:
        from_attributes = True