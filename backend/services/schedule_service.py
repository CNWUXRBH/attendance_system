from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from fastapi import HTTPException

from models import schedule as schedule_model
from schemas import schedule as schedule_schema

def check_schedule_conflict(db: Session, employee_id: int, start_date: date, end_date: date, schedule_id: Optional[int] = None):
    query = db.query(schedule_model.Schedule).filter(
        schedule_model.Schedule.employee_id == employee_id,
        schedule_model.Schedule.start_date <= end_date,
        schedule_model.Schedule.end_date >= start_date
    )
    if schedule_id:
        query = query.filter(schedule_model.Schedule.schedule_id != schedule_id)
    
    return query.first()

def create_schedule(db: Session, schedule: schedule_schema.ScheduleCreate):
    conflict = check_schedule_conflict(db, employee_id=schedule.employee_id, start_date=schedule.start_date, end_date=schedule.end_date)
    if conflict:
        raise HTTPException(status_code=409, detail=f"Schedule conflict with existing schedule (ID: {conflict.schedule_id}) from {conflict.start_date} to {conflict.end_date}")
    
    db_schedule = schedule_model.Schedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def get_schedules(db: Session, skip: int = 0, limit: int = 100, employee_id: Optional[int] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, year: Optional[int] = None, month: Optional[int] = None):
    from sqlalchemy import extract, and_
    from models.employee import Employee
    from models.shift_type import ShiftType
    
    query = db.query(
        schedule_model.Schedule,
        Employee.name.label('employee_name'),
        ShiftType.name.label('shift_type_name')
    ).join(Employee, schedule_model.Schedule.employee_id == Employee.employee_id)\
     .join(ShiftType, schedule_model.Schedule.shift_type_id == ShiftType.shift_type_id)
    
    if employee_id:
        query = query.filter(schedule_model.Schedule.employee_id == employee_id)
    if start_date:
        query = query.filter(schedule_model.Schedule.start_date >= start_date)
    if end_date:
        query = query.filter(schedule_model.Schedule.end_date <= end_date)
    
    # 如果提供了year和month参数，按年月筛选
    if year and month:
        query = query.filter(
            and_(
                extract('year', schedule_model.Schedule.start_date) == year,
                extract('month', schedule_model.Schedule.start_date) == month
            )
        )
    
    results = query.offset(skip).limit(limit).all()
    
    # 如果是按年月查询，返回按日期分组的格式
    if year and month:
        schedules_by_date = {}
        for result in results:
            schedule, employee_name, shift_type_name = result
            date_str = schedule.start_date.strftime('%Y-%m-%d')
            
            if date_str not in schedules_by_date:
                schedules_by_date[date_str] = []
            
            schedules_by_date[date_str].append({
                'id': schedule.schedule_id,
                'employee_id': schedule.employee_id,
                'employee_name': employee_name,
                'shift_type_id': schedule.shift_type_id,
                'shift_type_name': shift_type_name,
                'start_date': schedule.start_date,
                'end_date': schedule.end_date,
                'status': schedule.status
            })
        
        return {'data': schedules_by_date}
    
    # 普通查询返回列表格式
    schedules = []
    for result in results:
        schedule, employee_name, shift_type_name = result
        schedules.append({
            'id': schedule.schedule_id,
            'employee_id': schedule.employee_id,
            'employee_name': employee_name,
            'shift_type_id': schedule.shift_type_id,
            'shift_type_name': shift_type_name,
            'start_date': schedule.start_date,
            'end_date': schedule.end_date,
            'status': schedule.status
        })
    
    return schedules

def get_schedule(db: Session, schedule_id: int):
    return db.query(schedule_model.Schedule).filter(schedule_model.Schedule.schedule_id == schedule_id).first()

def update_schedule(db: Session, schedule_id: int, schedule: schedule_schema.ScheduleCreate):
    db_schedule = get_schedule(db, schedule_id)
    if not db_schedule:
        return None

    conflict = check_schedule_conflict(db, employee_id=schedule.employee_id, start_date=schedule.start_date, end_date=schedule.end_date, schedule_id=schedule_id)
    if conflict:
        raise HTTPException(status_code=409, detail=f"Schedule conflict with existing schedule (ID: {conflict.schedule_id}) from {conflict.start_date} to {conflict.end_date}")

    for key, value in schedule.dict().items():
        setattr(db_schedule, key, value)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_schedule(db: Session, schedule_id: int):
    db_schedule = get_schedule(db, schedule_id)
    if db_schedule:
        db.delete(db_schedule)
        db.commit()
    return db_schedule

def create_batch_schedules(db: Session, schedules: List[schedule_schema.ScheduleCreate]):
    """批量创建排班"""
    created_schedules = []
    
    for schedule_data in schedules:
        # 检查每个排班的冲突
        conflict = check_schedule_conflict(
            db, 
            employee_id=schedule_data.employee_id, 
            start_date=schedule_data.start_date, 
            end_date=schedule_data.end_date
        )
        if conflict:
            raise HTTPException(
                status_code=409, 
                detail=f"Schedule conflict for employee {schedule_data.employee_id}: {conflict.start_date} to {conflict.end_date}"
            )
        
        # 创建排班
        db_schedule = schedule_model.Schedule(**schedule_data.dict())
        db.add(db_schedule)
        created_schedules.append(db_schedule)
    
    db.commit()
    for schedule in created_schedules:
        db.refresh(schedule)
    
    return created_schedules

def copy_schedule(db: Session, source_schedule_id: int, target_dates: List[date]):
    """复制排班到指定日期"""
    source_schedule = get_schedule(db, source_schedule_id)
    if not source_schedule:
        raise HTTPException(status_code=404, detail="Source schedule not found")
    
    copied_schedules = []
    
    for target_date in target_dates:
        # 计算目标日期的结束时间
        duration = source_schedule.end_date - source_schedule.start_date
        target_end_date = target_date + duration
        
        # 检查冲突
        conflict = check_schedule_conflict(
            db,
            employee_id=source_schedule.employee_id,
            start_date=target_date,
            end_date=target_end_date
        )
        if conflict:
            raise HTTPException(
                status_code=409,
                detail=f"Schedule conflict for date {target_date}: existing schedule from {conflict.start_date} to {conflict.end_date}"
            )
        
        # 创建新排班
        new_schedule = schedule_model.Schedule(
            employee_id=source_schedule.employee_id,
            shift_type_id=source_schedule.shift_type_id,
            start_date=target_date,
            end_date=target_end_date,
            status=source_schedule.status
        )
        db.add(new_schedule)
        copied_schedules.append(new_schedule)
    
    db.commit()
    for schedule in copied_schedules:
        db.refresh(schedule)
    
    return {"copied_count": len(copied_schedules), "schedules": copied_schedules}