from pydantic import BaseModel

class CompensatoryTimeRuleBase(BaseModel):
    name: str
    conversion_rate: float

class CompensatoryTimeRuleCreate(CompensatoryTimeRuleBase):
    pass

class CompensatoryTimeRule(CompensatoryTimeRuleBase):
    rule_id: int

    class Config:
        from_attributes = True