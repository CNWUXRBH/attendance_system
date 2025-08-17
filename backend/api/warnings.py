from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from database.database import get_db
from schemas import warnings as warnings_schema, notification as notification_schema
from services import warning_service, notification_service

router = APIRouter()

@router.post("/", response_model=warnings_schema.Warning)
def create_warning(warning: warnings_schema.WarningCreate, db: Session = Depends(get_db)):
    db_warning = warning_service.create_warning(db=db, warning=warning)
    # 创建警告后发送邮件预警
    notification_message = f"考勤异常预警：{db_warning.warning_type} - {db_warning.description}"
    notification = notification_schema.NotificationCreate(
        employee_id=db_warning.employee_id,
        message=notification_message,
        type="warning"
    )
    notification_service.create_notification(db=db, notification=notification)
    return db_warning

@router.get("/", response_model=List[warnings_schema.Warning])
def read_warnings(
    skip: int = 0,
    limit: int = 100,
    employee_id: int = None,
    warning_type: str = None,
    warning_date: date = None,
    db: Session = Depends(get_db)
):
    warnings = warning_service.get_warnings(db, skip=skip, limit=limit, employee_id=employee_id, warning_type=warning_type, warning_date=warning_date)
    return warnings

@router.get("/{warning_id}", response_model=warnings_schema.Warning)
def read_warning(warning_id: int, db: Session = Depends(get_db)):
    db_warning = warning_service.get_warning(db, warning_id=warning_id)
    if db_warning is None:
        raise HTTPException(status_code=404, detail="Warning not found")
    return db_warning

@router.put("/{warning_id}", response_model=warnings_schema.Warning)
def update_warning(warning_id: int, warning: warnings_schema.WarningCreate, db: Session = Depends(get_db)):
    db_warning = warning_service.update_warning(db, warning_id=warning_id, warning=warning)
    if db_warning is None:
        raise HTTPException(status_code=404, detail="Warning not found")
    return db_warning

@router.delete("/{warning_id}", response_model=warnings_schema.Warning)
def delete_warning(warning_id: int, db: Session = Depends(get_db)):
    db_warning = warning_service.delete_warning(db, warning_id=warning_id)
    if db_warning is None:
        raise HTTPException(status_code=404, detail="Warning not found")
    return db_warning

@router.post("/generate")
def generate_warnings(db: Session = Depends(get_db)):
    """
    Triggers the warning generation process.
    This endpoint checks all attendance records and generates new warnings based on the rules.
    """
    warning_service.check_and_generate_warnings(db)
    return {"message": "Warning generation process completed"}