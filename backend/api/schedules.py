from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database.database import get_db
from schemas import schedule as schedule_schema
from services import schedule_service

router = APIRouter()

@router.post("/", response_model=schedule_schema.Schedule)
def create_schedule(schedule: schedule_schema.ScheduleCreate, db: Session = Depends(get_db)):
    return schedule_service.create_schedule(db=db, schedule=schedule)

@router.get("/")
def read_schedules(
    skip: int = 0,
    limit: int = 100,
    employee_id: int = None,
    start_date: date = None,
    end_date: date = None,
    year: int = None,
    month: int = None,
    db: Session = Depends(get_db)
):
    schedules = schedule_service.get_schedules(
        db, skip=skip, limit=limit, employee_id=employee_id, 
        start_date=start_date, end_date=end_date, year=year, month=month
    )
    return schedules

@router.get("/{schedule_id}", response_model=schedule_schema.Schedule)
def read_schedule(schedule_id: int, db: Session = Depends(get_db)):
    db_schedule = schedule_service.get_schedule(db, schedule_id=schedule_id)
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

@router.put("/{schedule_id}", response_model=schedule_schema.Schedule)
def update_schedule(schedule_id: int, schedule: schedule_schema.ScheduleCreate, db: Session = Depends(get_db)):
    db_schedule = schedule_service.update_schedule(db, schedule_id=schedule_id, schedule=schedule)
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

@router.delete("/{schedule_id}", response_model=schedule_schema.Schedule)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    db_schedule = schedule_service.delete_schedule(db, schedule_id=schedule_id)
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

@router.post("/batch", response_model=List[schedule_schema.Schedule])
def create_batch_schedules(schedules: List[schedule_schema.ScheduleCreate], db: Session = Depends(get_db)):
    """批量创建排班"""
    return schedule_service.create_batch_schedules(db=db, schedules=schedules)

@router.post("/copy")
def copy_schedule(source_schedule_id: int, target_dates: List[date], db: Session = Depends(get_db)):
    """复制排班到指定日期"""
    return schedule_service.copy_schedule(db=db, source_schedule_id=source_schedule_id, target_dates=target_dates)

@router.get("/conflicts")
def check_conflicts(employee_id: int, start_date: date, end_date: date, schedule_id: Optional[int] = None, db: Session = Depends(get_db)):
    """检测排班冲突"""
    return schedule_service.check_schedule_conflict(db=db, employee_id=employee_id, start_date=start_date, end_date=end_date, schedule_id=schedule_id)