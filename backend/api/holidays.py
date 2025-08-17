from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas import holiday as holiday_schema
from services import holiday_service

router = APIRouter()

@router.post("/", response_model=holiday_schema.Holiday)
def create_holiday(holiday: holiday_schema.HolidayCreate, db: Session = Depends(get_db)):
    return holiday_service.create_holiday(db=db, holiday=holiday)

@router.get("/", response_model=List[holiday_schema.Holiday])
def read_holidays(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    holidays = holiday_service.get_holidays(db, skip=skip, limit=limit)
    return holidays

@router.get("/{holiday_id}", response_model=holiday_schema.Holiday)
def read_holiday(holiday_id: int, db: Session = Depends(get_db)):
    db_holiday = holiday_service.get_holiday(db, holiday_id=holiday_id)
    if db_holiday is None:
        raise HTTPException(status_code=404, detail="Holiday not found")
    return db_holiday

@router.put("/{holiday_id}", response_model=holiday_schema.Holiday)
def update_holiday(holiday_id: int, holiday: holiday_schema.HolidayCreate, db: Session = Depends(get_db)):
    db_holiday = holiday_service.update_holiday(db, holiday_id=holiday_id, holiday=holiday)
    if db_holiday is None:
        raise HTTPException(status_code=404, detail="Holiday not found")
    return db_holiday

@router.delete("/{holiday_id}", response_model=holiday_schema.Holiday)
def delete_holiday(holiday_id: int, db: Session = Depends(get_db)):
    db_holiday = holiday_service.delete_holiday(db, holiday_id=holiday_id)
    if db_holiday is None:
        raise HTTPException(status_code=404, detail="Holiday not found")
    return db_holiday