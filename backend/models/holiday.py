from sqlalchemy import Column, Integer, String, Date, func, DATETIME
from database.database import Base

class Holiday(Base):
    __tablename__ = "holidays"

    holiday_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    date = Column(Date, nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # e.g., 'legal', 'company'
    description = Column(String(255))
    created_at = Column(DATETIME, server_default=func.now())
    updated_at = Column(DATETIME, server_default=func.now(), onupdate=func.now())