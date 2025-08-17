from sqlalchemy.orm import Session
from typing import List, Optional

from models import holiday as holiday_model
from schemas import holiday as holiday_schema

def create_holiday(db: Session, holiday: holiday_schema.HolidayCreate):
    db_holiday = holiday_model.Holiday(**holiday.dict())
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)
    return db_holiday

def get_holidays(db: Session, skip: int = 0, limit: int = 100):
    return db.query(holiday_model.Holiday).offset(skip).limit(limit).all()

def get_holiday(db: Session, holiday_id: int):
    return db.query(holiday_model.Holiday).filter(holiday_model.Holiday.holiday_id == holiday_id).first()

def update_holiday(db: Session, holiday_id: int, holiday: holiday_schema.HolidayCreate):
    db_holiday = get_holiday(db, holiday_id)
    if db_holiday:
        for key, value in holiday.dict().items():
            setattr(db_holiday, key, value)
        db.commit()
        db.refresh(db_holiday)
    return db_holiday

def delete_holiday(db: Session, holiday_id: int):
    db_holiday = get_holiday(db, holiday_id)
    if db_holiday:
        db.delete(db_holiday)
        db.commit()
    return db_holiday