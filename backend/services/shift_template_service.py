from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta, datetime, time
from fastapi import HTTPException

from models import shift_template as shift_template_model
from models import schedule as schedule_model
from models import shift_type as shift_type_model
from schemas import shift_template as shift_template_schema
from services import schedule_service

def create_shift_template(db: Session, shift_template: shift_template_schema.ShiftTemplateCreate):
    db_shift_template = shift_template_model.ShiftTemplate(**shift_template.dict())
    db.add(db_shift_template)
    db.commit()
    db.refresh(db_shift_template)
    return db_shift_template

def get_shift_templates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(shift_template_model.ShiftTemplate).offset(skip).limit(limit).all()

def get_shift_template(db: Session, shift_template_id: int):
    return db.query(shift_template_model.ShiftTemplate).filter(shift_template_model.ShiftTemplate.id == shift_template_id).first()

def update_shift_template(db: Session, shift_template_id: int, shift_template: shift_template_schema.ShiftTemplateCreate):
    db_shift_template = get_shift_template(db, shift_template_id)
    if db_shift_template:
        for key, value in shift_template.dict().items():
            setattr(db_shift_template, key, value)
        db.commit()
        db.refresh(db_shift_template)
    return db_shift_template

def delete_shift_template(db: Session, shift_template_id: int):
    db_shift_template = get_shift_template(db, shift_template_id)
    if db_shift_template:
        db.delete(db_shift_template)
        db.commit()
    return db_shift_template

def apply_template_to_schedules(
    db: Session, 
    template_id: int, 
    employee_ids: List[int], 
    start_date: date, 
    end_date: date
):
    """应用排班模板到指定员工和日期范围"""
    # 获取模板
    template = get_shift_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Shift template not found")
    
    # 根据模板的时间信息查找匹配的班次类型，如果找不到则使用默认值
    shift_type = db.query(shift_type_model.ShiftType).filter(
        shift_type_model.ShiftType.start_time == template.start_time,
        shift_type_model.ShiftType.end_time == template.end_time
    ).first()
    
    # 如果找不到匹配的班次类型，使用第一个可用的班次类型或创建默认值
    if not shift_type:
        shift_type = db.query(shift_type_model.ShiftType).first()
        if not shift_type:
            # 如果数据库中没有任何班次类型，创建一个默认的班次类型
            default_shift_type = shift_type_model.ShiftType(
                name="标准班次",
                start_time=template.start_time if isinstance(template.start_time, time) else time(9, 0),
                end_time=template.end_time if isinstance(template.end_time, time) else time(17, 0),
                description="系统自动创建的默认班次类型"
            )
            db.add(default_shift_type)
            db.commit()
            db.refresh(default_shift_type)
            shift_type_id = default_shift_type.shift_type_id
        else:
            shift_type_id = shift_type.shift_type_id
    else:
        shift_type_id = shift_type.shift_type_id
    
    created_schedules = []
    conflicts = []
    
    # 计算日期范围内的所有日期
    current_date = start_date
    while current_date <= end_date:
        for employee_id in employee_ids:
            # 根据模板创建排班时间
            schedule_start = datetime.combine(
                current_date, 
                template.start_time if isinstance(template.start_time, time) else time(9, 0)
            )
            
            schedule_end = datetime.combine(
                current_date, 
                template.end_time if isinstance(template.end_time, time) else time(17, 0)
            )
            
            # 如果结束时间小于开始时间，说明跨天
            if template.end_time < template.start_time:
                schedule_end += timedelta(days=1)
            
            # 检查冲突
            conflict = schedule_service.check_schedule_conflict(
                db,
                employee_id=employee_id,
                start_date=schedule_start,
                end_date=schedule_end
            )
            
            if conflict:
                conflicts.append({
                    "employee_id": employee_id,
                    "date": current_date,
                    "conflict_schedule": {
                        "start_date": conflict.start_date,
                        "end_date": conflict.end_date
                    }
                })
            else:
                # 创建排班
                new_schedule = schedule_model.Schedule(
                    employee_id=employee_id,
                    shift_type_id=shift_type_id,
                    start_date=schedule_start,
                    end_date=schedule_end,
                    status=1  # 1表示已排班状态
                )
                db.add(new_schedule)
                created_schedules.append(new_schedule)
        
        current_date += timedelta(days=1)
    
    # 提交所有创建的排班
    if created_schedules:
        db.commit()
        for schedule in created_schedules:
            db.refresh(schedule)
    
    return {
        "created_count": len(created_schedules),
        "created_schedules": created_schedules,
        "conflicts_count": len(conflicts),
        "conflicts": conflicts
    }