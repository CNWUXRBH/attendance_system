from sqlalchemy import Column, Integer, String, Float
from database.database import Base

class CompensatoryTimeRule(Base):
    __tablename__ = "compensatory_time_rules"

    rule_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    conversion_rate = Column(Float, nullable=False)