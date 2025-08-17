from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import HTTPException, UploadFile
import logging
import pandas as pd
import io

from models import schedule as schedule_model
from models.schedule import ScheduleStatus, SchedulePriority
from models import employee as employee_model
from models import shift_type as shift_type_model
from schemas import schedule as schedule_schema

# 配置日志
logger = logging.getLogger(__name__)

def check_schedule_conflict(
    db: Session, 
    employee_id: int, 
    start_date: datetime, 
    end_date: datetime, 
    schedule_id: Optional[int] = None,
    check_type: str = "overlap"  # overlap, adjacent, minimum_rest
) -> Optional[schedule_model.Schedule]:
    """
    增强的排班冲突检测算法
    
    Args:
        db: 数据库会话
        employee_id: 员工ID
        start_date: 开始时间
        end_date: 结束时间
        schedule_id: 排除的排班ID（用于更新时）
        check_type: 检测类型 - overlap(重叠), adjacent(相邻), minimum_rest(最小休息时间)
    
    Returns:
        冲突的排班记录，如果没有冲突返回None
    """
    query = db.query(schedule_model.Schedule).filter(
        schedule_model.Schedule.employee_id == employee_id
    )
    
    if schedule_id:
        query = query.filter(schedule_model.Schedule.schedule_id != schedule_id)
    
    if check_type == "overlap":
        # 检查时间重叠
        query = query.filter(
            and_(
                schedule_model.Schedule.start_date < end_date,
                schedule_model.Schedule.end_date > start_date
            )
        )
    elif check_type == "adjacent":
        # 检查相邻时间（无间隔）
        query = query.filter(
            or_(
                schedule_model.Schedule.end_date == start_date,
                schedule_model.Schedule.start_date == end_date
            )
        )
    elif check_type == "minimum_rest":
        # 检查最小休息时间（8小时）
        min_rest_hours = 8
        min_rest_before = start_date - timedelta(hours=min_rest_hours)
        min_rest_after = end_date + timedelta(hours=min_rest_hours)
        
        query = query.filter(
            or_(
                # 前一个班次结束时间距离新班次开始时间不足8小时
                and_(
                    schedule_model.Schedule.end_date > min_rest_before,
                    schedule_model.Schedule.end_date <= start_date
                ),
                # 后一个班次开始时间距离新班次结束时间不足8小时
                and_(
                    schedule_model.Schedule.start_date < min_rest_after,
                    schedule_model.Schedule.start_date >= end_date
                )
            )
        )
    
    return query.first()

def check_multiple_conflicts(
    db: Session, 
    employee_id: int, 
    start_date: datetime, 
    end_date: datetime, 
    schedule_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    综合冲突检测，返回详细的冲突信息
    """
    conflicts = {
        "has_conflict": False,
        "overlap_conflict": None,
        "rest_time_conflict": None,
        "daily_hours_exceeded": False,
        "weekly_hours_exceeded": False,
        "details": []
    }
    
    # 检查时间重叠冲突
    overlap_conflict = check_schedule_conflict(
        db, employee_id, start_date, end_date, schedule_id, "overlap"
    )
    if overlap_conflict:
        conflicts["has_conflict"] = True
        conflicts["overlap_conflict"] = overlap_conflict
        conflicts["details"].append(f"与排班ID {overlap_conflict.schedule_id} 时间重叠")
    
    # 检查最小休息时间
    rest_conflict = check_schedule_conflict(
        db, employee_id, start_date, end_date, schedule_id, "minimum_rest"
    )
    if rest_conflict:
        conflicts["has_conflict"] = True
        conflicts["rest_time_conflict"] = rest_conflict
        conflicts["details"].append(f"与排班ID {rest_conflict.schedule_id} 休息时间不足8小时")
    
    # 检查当日工作时长是否超过限制（12小时）
    work_duration = (end_date - start_date).total_seconds() / 3600
    if work_duration > 12:
        conflicts["has_conflict"] = True
        conflicts["daily_hours_exceeded"] = True
        conflicts["details"].append(f"单次排班时长 {work_duration:.1f} 小时超过12小时限制")
    
    # 检查当日总工作时长
    daily_schedules = db.query(schedule_model.Schedule).filter(
        and_(
            schedule_model.Schedule.employee_id == employee_id,
            func.date(schedule_model.Schedule.start_date) == start_date.date()
        )
    )
    if schedule_id:
        daily_schedules = daily_schedules.filter(
            schedule_model.Schedule.schedule_id != schedule_id
        )
    
    total_daily_hours = work_duration
    for schedule in daily_schedules.all():
        duration = (schedule.end_date - schedule.start_date).total_seconds() / 3600
        total_daily_hours += duration
    
    if total_daily_hours > 12:
        conflicts["has_conflict"] = True
        conflicts["daily_hours_exceeded"] = True
        conflicts["details"].append(f"当日总工作时长 {total_daily_hours:.1f} 小时超过12小时限制")
    
    return conflicts

def create_schedule(db: Session, schedule: schedule_schema.ScheduleCreate):
    """创建单个排班，使用增强的冲突检测"""
    # 使用综合冲突检测
    conflicts = check_multiple_conflicts(
        db,
        employee_id=schedule.employee_id,
        start_date=schedule.start_date,
        end_date=schedule.end_date
    )
    
    if conflicts["has_conflict"]:
        raise HTTPException(
            status_code=409,
            detail=f"排班冲突: {'; '.join(conflicts['details'])}"
        )
    
    try:
        db_schedule = schedule_model.Schedule(**schedule.dict())
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except Exception as e:
        db.rollback()
        logger.error(f"创建排班失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建排班失败: {str(e)}")

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
    """更新排班，使用增强的冲突检测"""
    db_schedule = get_schedule(db, schedule_id)
    if not db_schedule:
        return None

    # 使用综合冲突检测（排除当前排班）
    conflicts = check_multiple_conflicts(
        db,
        employee_id=schedule.employee_id,
        start_date=schedule.start_date,
        end_date=schedule.end_date,
        schedule_id=schedule_id
    )
    
    if conflicts["has_conflict"]:
        raise HTTPException(
            status_code=409,
            detail=f"排班冲突: {'; '.join(conflicts['details'])}"
        )

    try:
        for key, value in schedule.dict().items():
            setattr(db_schedule, key, value)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except Exception as e:
        db.rollback()
        logger.error(f"更新排班失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新排班失败: {str(e)}")

def delete_schedule(db: Session, schedule_id: int):
    db_schedule = get_schedule(db, schedule_id)
    if db_schedule:
        db.delete(db_schedule)
        db.commit()
    return db_schedule

def create_batch_schedules(
    db: Session, 
    schedules: List[schedule_schema.ScheduleCreate],
    ignore_conflicts: bool = False,
    validate_only: bool = False
) -> Dict[str, Any]:
    """
    改进的批量创建排班，支持事务回滚和详细的冲突报告
    
    Args:
        db: 数据库会话
        schedules: 排班数据列表
        ignore_conflicts: 是否忽略冲突（跳过冲突的排班）
        validate_only: 仅验证不实际创建
    
    Returns:
        包含创建结果和冲突信息的字典
    """
    result = {
        "success_count": 0,
        "conflict_count": 0,
        "error_count": 0,
        "created_schedules": [],
        "conflicts": [],
        "errors": []
    }
    
    created_schedules = []
    
    try:
        # 开始事务
        for i, schedule_data in enumerate(schedules):
            try:
                # 综合冲突检测
                conflicts = check_multiple_conflicts(
                    db,
                    employee_id=schedule_data.employee_id,
                    start_date=schedule_data.start_date,
                    end_date=schedule_data.end_date
                )
                
                if conflicts["has_conflict"]:
                    result["conflict_count"] += 1
                    conflict_info = {
                        "index": i,
                        "employee_id": schedule_data.employee_id,
                        "start_date": schedule_data.start_date,
                        "end_date": schedule_data.end_date,
                        "details": conflicts["details"]
                    }
                    result["conflicts"].append(conflict_info)
                    
                    if not ignore_conflicts:
                        raise HTTPException(
                            status_code=409,
                            detail=f"排班冲突 (索引 {i}): {'; '.join(conflicts['details'])}"
                        )
                    else:
                        logger.warning(f"跳过冲突排班: {conflict_info}")
                        continue
                
                # 如果只是验证，不实际创建
                if validate_only:
                    result["success_count"] += 1
                    continue
                
                # 创建排班记录
                db_schedule = schedule_model.Schedule(**schedule_data.dict())
                db.add(db_schedule)
                created_schedules.append(db_schedule)
                result["success_count"] += 1
                
            except HTTPException:
                raise  # 重新抛出HTTP异常
            except Exception as e:
                result["error_count"] += 1
                error_info = {
                    "index": i,
                    "employee_id": schedule_data.employee_id,
                    "error": str(e)
                }
                result["errors"].append(error_info)
                logger.error(f"创建排班时发生错误: {error_info}")
                
                if not ignore_conflicts:
                    raise HTTPException(
                        status_code=500,
                        detail=f"创建排班时发生错误 (索引 {i}): {str(e)}"
                    )
        
        # 如果不是仅验证模式，提交事务
        if not validate_only and created_schedules:
            db.commit()
            
            # 刷新所有创建的对象
            for schedule in created_schedules:
                db.refresh(schedule)
                result["created_schedules"].append({
                    "schedule_id": schedule.schedule_id,
                    "employee_id": schedule.employee_id,
                    "start_date": schedule.start_date,
                    "end_date": schedule.end_date,
                    "status": schedule.status
                })
        
        return result
        
    except Exception as e:
        # 发生错误时回滚事务
        db.rollback()
        logger.error(f"批量创建排班失败，已回滚事务: {str(e)}")
        raise e

def copy_schedule(
    db: Session, 
    source_schedule_id: int, 
    target_dates: List[date],
    ignore_conflicts: bool = False
) -> Dict[str, Any]:
    """复制排班到指定日期，支持冲突处理和事务回滚"""
    source_schedule = get_schedule(db, source_schedule_id)
    if not source_schedule:
        raise HTTPException(status_code=404, detail="源排班记录未找到")
    
    result = {
        "success_count": 0,
        "conflict_count": 0,
        "error_count": 0,
        "created_schedules": [],
        "conflicts": [],
        "errors": []
    }
    
    created_schedules = []
    
    try:
        for i, target_date in enumerate(target_dates):
            try:
                # 计算目标日期的时间
                duration = source_schedule.end_date - source_schedule.start_date
                target_start = datetime.combine(target_date, source_schedule.start_date.time())
                target_end = target_start + duration
                
                # 综合冲突检测
                conflicts = check_multiple_conflicts(
                    db,
                    employee_id=source_schedule.employee_id,
                    start_date=target_start,
                    end_date=target_end
                )
                
                if conflicts["has_conflict"]:
                    result["conflict_count"] += 1
                    conflict_info = {
                        "target_date": target_date,
                        "employee_id": source_schedule.employee_id,
                        "details": conflicts["details"]
                    }
                    result["conflicts"].append(conflict_info)
                    
                    if not ignore_conflicts:
                        raise HTTPException(
                            status_code=409,
                            detail=f"复制到日期 {target_date} 时发生冲突: {'; '.join(conflicts['details'])}"
                        )
                    else:
                        logger.warning(f"跳过冲突日期: {conflict_info}")
                        continue
                
                # 创建新排班
                new_schedule = schedule_model.Schedule(
                    employee_id=source_schedule.employee_id,
                    shift_type_id=source_schedule.shift_type_id,
                    start_date=target_start,
                    end_date=target_end,
                    status=source_schedule.status
                )
                
                db.add(new_schedule)
                created_schedules.append(new_schedule)
                result["success_count"] += 1
                
            except HTTPException:
                raise  # 重新抛出HTTP异常
            except Exception as e:
                result["error_count"] += 1
                error_info = {
                    "target_date": target_date,
                    "error": str(e)
                }
                result["errors"].append(error_info)
                logger.error(f"复制排班到日期 {target_date} 时发生错误: {str(e)}")
                
                if not ignore_conflicts:
                    raise HTTPException(
                        status_code=500,
                        detail=f"复制排班到日期 {target_date} 时发生错误: {str(e)}"
                    )
        
        # 提交事务
        if created_schedules:
            db.commit()
            
            # 刷新所有创建的对象
            for schedule in created_schedules:
                db.refresh(schedule)
                result["created_schedules"].append({
                    "schedule_id": schedule.schedule_id,
                    "employee_id": schedule.employee_id,
                    "start_date": schedule.start_date,
                    "end_date": schedule.end_date,
                    "status": schedule.status
                })
        
        return result
        
    except Exception as e:
        # 发生错误时回滚事务
        db.rollback()
        logger.error(f"复制排班失败，已回滚事务: {str(e)}")
        raise e

def transition_schedule_status(
    db: Session,
    schedule_id: int,
    transition_data: schedule_schema.ScheduleStatusTransition
) -> schedule_model.Schedule:
    """排班状态转换"""
    schedule = get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="排班记录未找到")
    
    # 检查状态转换是否有效
    if not schedule.can_transition_to(transition_data.new_status):
        raise HTTPException(
            status_code=400,
            detail=f"无法从状态 '{schedule.get_status_display()}' 转换到 '{transition_data.new_status.value}'"
        )
    
    try:
        # 更新状态
        schedule.status = transition_data.new_status
        
        # 更新备注
        if transition_data.notes:
            schedule.notes = transition_data.notes
        
        db.commit()
        db.refresh(schedule)
        return schedule
        
    except Exception as e:
        db.rollback()
        logger.error(f"状态转换失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"状态转换失败: {str(e)}")

def batch_status_operation(
    db: Session,
    operation_data: schedule_schema.ScheduleBatchOperation
) -> Dict[str, Any]:
    """批量状态操作"""
    result = {
        "success_count": 0,
        "error_count": 0,
        "updated_schedules": [],
        "errors": []
    }
    
    # 定义操作映射
    operation_mapping = {
        "complete": ScheduleStatus.COMPLETED,
        "cancel": ScheduleStatus.CANCELLED,
        "activate": ScheduleStatus.ACTIVE
    }
    
    if operation_data.operation not in operation_mapping:
        raise HTTPException(status_code=400, detail=f"不支持的操作: {operation_data.operation}")
    
    target_status = operation_mapping[operation_data.operation]
    
    try:
        for schedule_id in operation_data.schedule_ids:
            try:
                # 构建状态转换数据
                transition_data = schedule_schema.ScheduleStatusTransition(
                    new_status=target_status,
                    approved_by=operation_data.approved_by,
                    rejection_reason=operation_data.rejection_reason,
                    notes=operation_data.notes
                )
                
                # 执行状态转换
                updated_schedule = transition_schedule_status(db, schedule_id, transition_data)
                
                result["success_count"] += 1
                result["updated_schedules"].append({
                    "schedule_id": updated_schedule.schedule_id,
                    "employee_id": updated_schedule.employee_id,
                    "old_status": updated_schedule.status.value,
                    "new_status": target_status.value
                })
                
            except HTTPException as e:
                result["error_count"] += 1
                result["errors"].append({
                    "schedule_id": schedule_id,
                    "error": e.detail
                })
                logger.warning(f"批量操作中排班ID {schedule_id} 失败: {e.detail}")
            except Exception as e:
                result["error_count"] += 1
                result["errors"].append({
                    "schedule_id": schedule_id,
                    "error": str(e)
                })
                logger.error(f"批量操作中排班ID {schedule_id} 发生错误: {str(e)}")
        
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"批量状态操作失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量状态操作失败: {str(e)}")

def get_schedule_statistics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    employee_id: Optional[int] = None
) -> schedule_schema.ScheduleStatistics:
    """获取排班统计信息"""
    query = db.query(schedule_model.Schedule)
    
    # 应用过滤条件
    if start_date:
        query = query.filter(schedule_model.Schedule.start_date >= start_date)
    if end_date:
        query = query.filter(schedule_model.Schedule.end_date <= end_date)
    if employee_id:
        query = query.filter(schedule_model.Schedule.employee_id == employee_id)
    
    schedules = query.all()
    
    # 统计状态分布
    status_counts = {}
    for status in ScheduleStatus:
        status_counts[status.value] = sum(1 for s in schedules if s.status == status)
    
    # 统计优先级分布
    priority_counts = {}
    for priority in SchedulePriority:
        priority_counts[priority.value] = sum(1 for s in schedules if s.priority == priority)
    
    # 统计员工排班数量
    employee_schedule_counts = {}
    for schedule in schedules:
        emp_id = schedule.employee_id
        employee_schedule_counts[emp_id] = employee_schedule_counts.get(emp_id, 0) + 1
    
    # 统计每日排班数量
    daily_schedule_counts = {}
    for schedule in schedules:
        date_key = schedule.start_date.date().isoformat()
        daily_schedule_counts[date_key] = daily_schedule_counts.get(date_key, 0) + 1
    
    return schedule_schema.ScheduleStatistics(
        total_schedules=len(schedules),
        status_counts=status_counts,
        priority_counts=priority_counts,
        employee_schedule_counts=employee_schedule_counts,
        daily_schedule_counts=daily_schedule_counts
    )

def get_schedules_by_status(
    db: Session,
    status: ScheduleStatus,
    skip: int = 0,
    limit: int = 100
) -> List[schedule_model.Schedule]:
    """根据状态获取排班列表"""
    return db.query(schedule_model.Schedule).filter(
        schedule_model.Schedule.status == status
    ).offset(skip).limit(limit).all()

def get_active_schedules(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[schedule_model.Schedule]:
    """获取生效中的排班记录"""
    return get_schedules_by_status(db, ScheduleStatus.ACTIVE, skip, limit)

async def import_schedules_from_file(
    db: Session,
    file: UploadFile
) -> Dict[str, Any]:
    """从文件导入排班数据"""
    try:
        # 读取文件内容
        contents = await file.read()
        
        # 根据文件类型解析数据
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式")
        
        # 验证必需的列
        required_columns = ['employee_id', 'shift_type_id', 'start_date', 'end_date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"缺少必需的列: {', '.join(missing_columns)}"
            )
        
        success_count = 0
        error_count = 0
        errors = []
        
        # 逐行处理数据
        for index, row in df.iterrows():
            try:
                # 验证员工是否存在
                employee = db.query(employee_model.Employee).filter(
                    employee_model.Employee.employee_id == row['employee_id']
                ).first()
                if not employee:
                    errors.append(f"第{index+2}行: 员工ID {row['employee_id']} 不存在")
                    error_count += 1
                    continue
                
                # 验证班次类型是否存在
                shift_type = db.query(shift_type_model.ShiftType).filter(
                    shift_type_model.ShiftType.shift_type_id == row['shift_type_id']
                ).first()
                if not shift_type:
                    errors.append(f"第{index+2}行: 班次类型ID {row['shift_type_id']} 不存在")
                    error_count += 1
                    continue
                
                # 解析日期时间
                try:
                    if isinstance(row['start_date'], str):
                        start_date = datetime.strptime(row['start_date'], '%Y-%m-%d %H:%M:%S')
                    else:
                        start_date = pd.to_datetime(row['start_date'])
                    
                    if isinstance(row['end_date'], str):
                        end_date = datetime.strptime(row['end_date'], '%Y-%m-%d %H:%M:%S')
                    else:
                        end_date = pd.to_datetime(row['end_date'])
                except Exception as e:
                    errors.append(f"第{index+2}行: 日期格式错误 - {str(e)}")
                    error_count += 1
                    continue
                
                # 创建排班记录
                schedule_data = schedule_schema.ScheduleCreate(
                    employee_id=int(row['employee_id']),
                    shift_type_id=int(row['shift_type_id']),
                    start_date=start_date,
                    end_date=end_date,
                    notes=row.get('notes', ''),
                    priority=SchedulePriority.NORMAL
                )
                
                # 检查冲突（可选，根据需要启用）
                conflicts = check_multiple_conflicts(
                    db,
                    employee_id=schedule_data.employee_id,
                    start_date=schedule_data.start_date,
                    end_date=schedule_data.end_date
                )
                
                if conflicts["has_conflict"]:
                    errors.append(f"第{index+2}行: 排班冲突 - {'; '.join(conflicts['details'])}")
                    error_count += 1
                    continue
                
                # 创建排班记录
                db_schedule = schedule_model.Schedule(**schedule_data.dict())
                db.add(db_schedule)
                success_count += 1
                
            except Exception as e:
                errors.append(f"第{index+2}行: 处理错误 - {str(e)}")
                error_count += 1
                continue
        
        # 提交事务
        if success_count > 0:
            db.commit()
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10]  # 只返回前10个错误
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"导入排班文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")