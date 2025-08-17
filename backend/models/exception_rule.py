from sqlalchemy import Column, Integer, String, DATETIME, func
from database.database import Base

class ExceptionRule(Base):
    __tablename__ = "exception_rules"

    rule_id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(255), nullable=False)
    rule_type = Column(String(50), nullable=False)
    threshold = Column(Integer)
    description = Column(String(255))
    created_at = Column(DATETIME, server_default=func.now())
    updated_at = Column(DATETIME, server_default=func.now(), onupdate=func.now())