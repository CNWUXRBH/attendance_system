from sqlalchemy.orm import Session
from sqlalchemy import func
from models import attendance_record as attendance_model
from models import exception_rule as rule_model
from models import warnings as warning_model
from models import schedule as schedule_model
from schemas import warnings as warning_schema
from schemas import notification as notification_schema
from services import notification_service
from datetime import time, timedelta, datetime
from typing import List, Optional
from datetime import date

def create_warning(db: Session, warning: warning_schema.WarningCreate):
    db_warning = warning_model.Warning(**warning.dict())
    db.add(db_warning)
    db.commit()
    db.refresh(db_warning)
    return db_warning

def get_warnings(db: Session, skip: int = 0, limit: int = 100, employee_id: Optional[int] = None, warning_type: Optional[str] = None, warning_date: Optional[date] = None):
    query = db.query(warning_model.Warning)
    if employee_id:
        query = query.filter(warning_model.Warning.employee_id == employee_id)
    if warning_type:
        query = query.filter(warning_model.Warning.warning_type.contains(warning_type))
    if warning_date:
        query = query.filter(warning_model.Warning.date == warning_date)
    warnings = query.offset(skip).limit(limit).all()
    return warnings

def get_warning(db: Session, warning_id: int):
    return db.query(warning_model.Warning).filter(warning_model.Warning.warning_id == warning_id).first()

def update_warning(db: Session, warning_id: int, warning: warning_schema.WarningCreate):
    db_warning = get_warning(db, warning_id)
    if db_warning:
        for key, value in warning.dict().items():
            setattr(db_warning, key, value)
        db.commit()
        db.refresh(db_warning)
    return db_warning

def delete_warning(db: Session, warning_id: int):
    db_warning = get_warning(db, warning_id)
    if db_warning:
        db.delete(db_warning)
        db.commit()
    return db_warning

def check_and_generate_warnings(db: Session):
    rules = db.query(rule_model.ExceptionRule).all()
    if not rules:
        return

    for rule in rules:
        if rule.rule_type == "late":
            handle_late_rule(db, rule)
        elif rule.rule_type == "early_leave":
            handle_early_leave_rule(db, rule)

def handle_late_rule(db: Session, rule: rule_model.ExceptionRule):
    # This is a simplified example. A real implementation would need to handle dates and timezones carefully.
    records = db.query(attendance_model.AttendanceRecord).filter(attendance_model.AttendanceRecord.clock_in_time.isnot(None)).all()
    
    for record in records:
        schedule = db.query(schedule_model.Schedule).filter(schedule_model.Schedule.employee_id == record.employee_id, func.date(schedule_model.Schedule.schedule_date) == record.clock_in_time.date()).first()
        if schedule and schedule.shift_type:
            late_threshold = (datetime.combine(datetime.today(), schedule.shift_type.start_time) + timedelta(minutes=rule.minutes_threshold)).time()
            if record.clock_in_time.time() > late_threshold:
                existing_warning = db.query(warning_model.Warning).filter(warning_model.Warning.employee_id == record.employee_id, warning_model.Warning.warning_type == 'late', func.date(warning_model.Warning.created_at) == record.clock_in_time.date()).first()
                if not existing_warning:
                    new_warning = warning_model.Warning(
                        employee_id=record.employee_id,
                        warning_type="late",
                        description=f"Late arrival on {record.clock_in_time.date()}",
                        status="pending"
                    )
                    db.add(new_warning)
                    db.commit()
                    db.refresh(new_warning)
                    # 直接发送邮件预警
                    notification_message = f"考勤异常预警：迟到 - {new_warning.description}"
                    notification = notification_schema.NotificationCreate(
                        employee_id=new_warning.employee_id,
                        message=notification_message,
                        type="warning"
                    )
                    notification_service.create_notification(db=db, notification=notification)

def handle_early_leave_rule(db: Session, rule: rule_model.ExceptionRule):
    records = db.query(attendance_model.AttendanceRecord).filter(attendance_model.AttendanceRecord.clock_out_time.isnot(None)).all()

    for record in records:
        schedule = db.query(schedule_model.Schedule).filter(schedule_model.Schedule.employee_id == record.employee_id, func.date(schedule_model.Schedule.schedule_date) == record.clock_out_time.date()).first()
        if schedule and schedule.shift_type:
            early_leave_threshold = (datetime.combine(datetime.today(), schedule.shift_type.end_time) - timedelta(minutes=rule.minutes_threshold)).time()
            if record.clock_out_time.time() < early_leave_threshold:
                existing_warning = db.query(warning_model.Warning).filter(warning_model.Warning.employee_id == record.employee_id, warning_model.Warning.warning_type == 'early_leave', func.date(warning_model.Warning.created_at) == record.clock_out_time.date()).first()
                if not existing_warning:
                    new_warning = warning_model.Warning(
                        employee_id=record.employee_id,
                        warning_type="early_leave",
                        description=f"Early leave on {record.clock_out_time.date()}",
                        status="pending"
                    )
                    db.add(new_warning)
                    db.commit()
                    db.refresh(new_warning)
                    # 直接发送邮件预警
                    notification_message = f"考勤异常预警：早退 - {new_warning.description}"
                    notification = notification_schema.NotificationCreate(
                        employee_id=new_warning.employee_id,
                        message=notification_message,
                        type="warning"
                    )
                    notification_service.create_notification(db=db, notification=notification)