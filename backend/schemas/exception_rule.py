from pydantic import BaseModel
from typing import Optional

class ExceptionRuleBase(BaseModel):
    rule_name: str
    rule_type: str
    threshold: Optional[int] = None
    description: Optional[str] = None

class ExceptionRuleCreate(ExceptionRuleBase):
    pass

class ExceptionRule(ExceptionRuleBase):
    rule_id: int

    class Config:
        from_attributes = True