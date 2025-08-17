from sqlalchemy import Column, Integer, String, TIME, DATETIME, func
from database.database import Base

class ShiftType(Base):
    __tablename__ = "shift_types"

    shift_type_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    start_time = Column(TIME)
    end_time = Column(TIME)
    description = Column(String(255))
    created_at = Column(DATETIME, default=func.now())
    updated_at = Column(DATETIME, default=func.now(), onupdate=func.now())