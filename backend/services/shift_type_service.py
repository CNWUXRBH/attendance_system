from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import time
from fastapi import HTTPException

from models import shift_type as shift_type_model
from schemas import shift_type as shift_type_schema

def create_shift_type(db: Session, shift_type: shift_type_schema.ShiftTypeCreate):
    """创建新的班次类型"""
    # 检查名称是否已存在
    existing_shift_type = db.query(shift_type_model.ShiftType).filter(
        shift_type_model.ShiftType.name == shift_type.name
    ).first()
    if existing_shift_type:
        raise HTTPException(status_code=400, detail="班次类型名称已存在")
    
    # 检查时间冲突
    conflict = check_time_conflict(db, shift_type.start_time, shift_type.end_time)
    if conflict:
        raise HTTPException(
            status_code=400, 
            detail=f"时间段与现有班次类型 '{conflict.name}' 冲突"
        )
    
    db_shift_type = shift_type_model.ShiftType(**shift_type.dict())
    db.add(db_shift_type)
    db.commit()
    db.refresh(db_shift_type)
    return db_shift_type

def get_shift_types(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    name: Optional[str] = None
):
    """获取班次类型列表，支持按名称过滤"""
    query = db.query(shift_type_model.ShiftType)
    
    if name:
        query = query.filter(shift_type_model.ShiftType.name.contains(name))
    
    return query.offset(skip).limit(limit).all()

def get_shift_type(db: Session, shift_type_id: int):
    """根据ID获取班次类型"""
    return db.query(shift_type_model.ShiftType).filter(
        shift_type_model.ShiftType.shift_type_id == shift_type_id
    ).first()

def get_shift_type_by_name(db: Session, name: str):
    """根据名称获取班次类型"""
    return db.query(shift_type_model.ShiftType).filter(
        shift_type_model.ShiftType.name == name
    ).first()

def update_shift_type(
    db: Session, 
    shift_type_id: int, 
    shift_type: shift_type_schema.ShiftTypeCreate
):
    """更新班次类型"""
    db_shift_type = get_shift_type(db, shift_type_id)
    if not db_shift_type:
        return None
    
    # 检查名称是否与其他班次类型冲突
    existing_shift_type = db.query(shift_type_model.ShiftType).filter(
        and_(
            shift_type_model.ShiftType.name == shift_type.name,
            shift_type_model.ShiftType.shift_type_id != shift_type_id
        )
    ).first()
    if existing_shift_type:
        raise HTTPException(status_code=400, detail="班次类型名称已存在")
    
    # 检查时间冲突（排除当前班次类型）
    conflict = check_time_conflict(
        db, shift_type.start_time, shift_type.end_time, exclude_id=shift_type_id
    )
    if conflict:
        raise HTTPException(
            status_code=400, 
            detail=f"时间段与现有班次类型 '{conflict.name}' 冲突"
        )
    
    for key, value in shift_type.dict().items():
        setattr(db_shift_type, key, value)
    
    db.commit()
    db.refresh(db_shift_type)
    return db_shift_type

def delete_shift_type(db: Session, shift_type_id: int):
    """删除班次类型"""
    db_shift_type = get_shift_type(db, shift_type_id)
    if not db_shift_type:
        return None
    
    # 检查是否有关联的排班记录
    from models import schedule as schedule_model
    related_schedules = db.query(schedule_model.Schedule).filter(
        schedule_model.Schedule.shift_type_id == shift_type_id
    ).first()
    
    if related_schedules:
        raise HTTPException(
            status_code=400, 
            detail="无法删除班次类型，存在关联的排班记录"
        )
    
    db.delete(db_shift_type)
    db.commit()
    return db_shift_type

def get_active_shift_types(db: Session):
    """获取所有可用的班次类型"""
    return db.query(shift_type_model.ShiftType).order_by(
        shift_type_model.ShiftType.start_time
    ).all()

def create_batch_shift_types(
    db: Session, 
    shift_types: List[shift_type_schema.ShiftTypeCreate]
):
    """批量创建班次类型"""
    created_shift_types = []
    
    try:
        for shift_type in shift_types:
            # 检查名称是否已存在
            existing_shift_type = db.query(shift_type_model.ShiftType).filter(
                shift_type_model.ShiftType.name == shift_type.name
            ).first()
            if existing_shift_type:
                raise HTTPException(
                    status_code=400, 
                    detail=f"班次类型名称 '{shift_type.name}' 已存在"
                )
            
            # 检查时间冲突
            conflict = check_time_conflict(db, shift_type.start_time, shift_type.end_time)
            if conflict:
                raise HTTPException(
                    status_code=400, 
                    detail=f"班次类型 '{shift_type.name}' 的时间段与现有班次类型 '{conflict.name}' 冲突"
                )
            
            db_shift_type = shift_type_model.ShiftType(**shift_type.dict())
            db.add(db_shift_type)
            created_shift_types.append(db_shift_type)
        
        db.commit()
        
        # 刷新所有创建的对象
        for shift_type in created_shift_types:
            db.refresh(shift_type)
        
        return created_shift_types
    
    except Exception as e:
        db.rollback()
        raise e

def check_time_conflict(
    db: Session, 
    start_time: time, 
    end_time: time, 
    exclude_id: Optional[int] = None
):
    """检查时间段是否与现有班次类型冲突"""
    query = db.query(shift_type_model.ShiftType)
    
    if exclude_id:
        query = query.filter(shift_type_model.ShiftType.shift_type_id != exclude_id)
    
    # 检查时间重叠的逻辑
    # 两个时间段重叠的条件：
    # 1. 新时间段的开始时间在现有时间段内
    # 2. 新时间段的结束时间在现有时间段内
    # 3. 新时间段完全包含现有时间段
    # 4. 现有时间段完全包含新时间段
    
    # 处理跨天的情况
    if start_time > end_time:  # 跨天班次
        # 跨天班次与其他班次的冲突检测更复杂
        conflict = query.filter(
            or_(
                # 其他班次的开始时间在跨天班次的第一段内（当天晚上）
                shift_type_model.ShiftType.start_time >= start_time,
                # 其他班次的结束时间在跨天班次的第二段内（次日早上）
                shift_type_model.ShiftType.end_time <= end_time,
                # 其他班次也是跨天班次且有重叠
                and_(
                    shift_type_model.ShiftType.start_time > shift_type_model.ShiftType.end_time,
                    or_(
                        shift_type_model.ShiftType.start_time <= start_time,
                        shift_type_model.ShiftType.end_time >= end_time
                    )
                )
            )
        ).first()
    else:  # 正常班次（不跨天）
        conflict = query.filter(
            or_(
                # 新班次开始时间在现有班次时间段内
                and_(
                    shift_type_model.ShiftType.start_time <= start_time,
                    shift_type_model.ShiftType.end_time > start_time
                ),
                # 新班次结束时间在现有班次时间段内
                and_(
                    shift_type_model.ShiftType.start_time < end_time,
                    shift_type_model.ShiftType.end_time >= end_time
                ),
                # 新班次完全包含现有班次
                and_(
                    start_time <= shift_type_model.ShiftType.start_time,
                    end_time >= shift_type_model.ShiftType.end_time
                ),
                # 现有班次完全包含新班次
                and_(
                    shift_type_model.ShiftType.start_time <= start_time,
                    shift_type_model.ShiftType.end_time >= end_time
                )
            )
        ).first()
    
    return conflict

def get_shift_types_by_time_range(
    db: Session, 
    start_time: time, 
    end_time: time
):
    """根据时间范围获取班次类型"""
    if start_time <= end_time:
        # 正常时间范围
        return db.query(shift_type_model.ShiftType).filter(
            and_(
                shift_type_model.ShiftType.start_time >= start_time,
                shift_type_model.ShiftType.end_time <= end_time
            )
        ).all()
    else:
        # 跨天时间范围
        return db.query(shift_type_model.ShiftType).filter(
            or_(
                shift_type_model.ShiftType.start_time >= start_time,
                shift_type_model.ShiftType.end_time <= end_time
            )
        ).all()

def get_shift_type_statistics(db: Session):
    """获取班次类型统计信息"""
    from models import schedule as schedule_model
    from sqlalchemy import func
    
    # 统计每个班次类型的使用次数
    stats = db.query(
        shift_type_model.ShiftType.shift_type_id,
        shift_type_model.ShiftType.name,
        func.count(schedule_model.Schedule.schedule_id).label('usage_count')
    ).outerjoin(
        schedule_model.Schedule,
        shift_type_model.ShiftType.shift_type_id == schedule_model.Schedule.shift_type_id
    ).group_by(
        shift_type_model.ShiftType.shift_type_id,
        shift_type_model.ShiftType.name
    ).all()
    
    return [
        {
            "shift_type_id": stat.shift_type_id,
            "name": stat.name,
            "usage_count": stat.usage_count
        }
        for stat in stats
    ]