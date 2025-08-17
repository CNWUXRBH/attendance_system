from sqlalchemy import Column, Integer, String, Float, Time
from database.database import Base

class OvertimeRule(Base):
    __tablename__ = "overtime_rules"

    rule_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    rate = Column(Float, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)