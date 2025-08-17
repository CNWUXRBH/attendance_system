from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from database.database import get_db
from schemas import schedule as schedule_schema
from services import schedule_service
from models.schedule import ScheduleStatus

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
def update_schedule(schedule_id: int, schedule: schedule_schema.ScheduleUpdate, db: Session = Depends(get_db)):
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

@router.post("/batch", response_model=schedule_schema.BatchOperationResult)
def create_batch_schedules(
    schedules: List[schedule_schema.ScheduleCreate], 
    ignore_conflicts: bool = False,
    validate_only: bool = False,
    db: Session = Depends(get_db)
):
    """批量创建排班"""
    return schedule_service.create_batch_schedules(
        db=db, 
        schedules=schedules, 
        ignore_conflicts=ignore_conflicts,
        validate_only=validate_only
    )

@router.post("/copy", response_model=schedule_schema.BatchOperationResult)
def copy_schedule(
    source_schedule_id: int, 
    target_dates: List[date], 
    ignore_conflicts: bool = False,
    db: Session = Depends(get_db)
):
    """复制排班到指定日期"""
    return schedule_service.copy_schedule(
        db=db, 
        source_schedule_id=source_schedule_id, 
        target_dates=target_dates,
        ignore_conflicts=ignore_conflicts
    )

@router.get("/conflicts", response_model=schedule_schema.ScheduleConflictInfo)
def check_conflicts(
    employee_id: int, 
    start_date: datetime, 
    end_date: datetime, 
    schedule_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    """检查排班冲突"""
    return schedule_service.check_multiple_conflicts(
        db=db, 
        employee_id=employee_id, 
        start_date=start_date, 
        end_date=end_date, 
        schedule_id=schedule_id
    )

# 状态管理相关API
@router.put("/{schedule_id}/status", response_model=schedule_schema.Schedule)
def transition_schedule_status(
    schedule_id: int,
    transition_data: schedule_schema.ScheduleStatusTransition,
    db: Session = Depends(get_db)
):
    """排班状态转换"""
    return schedule_service.transition_schedule_status(
        db=db,
        schedule_id=schedule_id,
        transition_data=transition_data
    )

@router.post("/batch-status")
def batch_status_operation(
    operation_data: schedule_schema.ScheduleBatchOperation,
    db: Session = Depends(get_db)
):
    """批量状态操作"""
    return schedule_service.batch_status_operation(
        db=db,
        operation_data=operation_data
    )

@router.get("/status/{status}", response_model=List[schedule_schema.Schedule])
def get_schedules_by_status(
    status: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """根据状态获取排班列表"""
    try:
        schedule_status = ScheduleStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的状态: {status}")
    
    return schedule_service.get_schedules_by_status(
        db=db,
        status=schedule_status,
        skip=skip,
        limit=limit
    )

@router.get("/active", response_model=List[schedule_schema.Schedule])
def get_active_schedules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取生效中的排班列表"""
    return schedule_service.get_active_schedules(
        db=db,
        skip=skip,
        limit=limit
    )

# 统计相关API
@router.get("/statistics", response_model=schedule_schema.ScheduleStatistics)
def get_schedule_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取排班统计信息"""
    return schedule_service.get_schedule_statistics(
        db=db,
        start_date=start_date,
        end_date=end_date,
        employee_id=employee_id
    )

@router.post("/import")
async def import_schedules(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """导入排班数据"""
    return await schedule_service.import_schedules_from_file(db=db, file=file)