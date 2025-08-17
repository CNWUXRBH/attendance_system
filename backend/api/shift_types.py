from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database.database import get_db
from schemas import shift_type as shift_type_schema
from services import shift_type_service

router = APIRouter()

@router.post("/", response_model=shift_type_schema.ShiftType)
def create_shift_type(shift_type: shift_type_schema.ShiftTypeCreate, db: Session = Depends(get_db)):
    """创建新的班次类型"""
    return shift_type_service.create_shift_type(db=db, shift_type=shift_type)

@router.get("/", response_model=List[shift_type_schema.ShiftType])
def read_shift_types(
    skip: int = 0, 
    limit: int = 100, 
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取班次类型列表，支持按名称过滤"""
    return shift_type_service.get_shift_types(db, skip=skip, limit=limit, name=name)

@router.get("/{shift_type_id}", response_model=shift_type_schema.ShiftType)
def read_shift_type(shift_type_id: int, db: Session = Depends(get_db)):
    """根据ID获取班次类型详情"""
    db_shift_type = shift_type_service.get_shift_type(db, shift_type_id=shift_type_id)
    if db_shift_type is None:
        raise HTTPException(status_code=404, detail="班次类型不存在")
    return db_shift_type

@router.put("/{shift_type_id}", response_model=shift_type_schema.ShiftType)
def update_shift_type(
    shift_type_id: int, 
    shift_type: shift_type_schema.ShiftTypeCreate, 
    db: Session = Depends(get_db)
):
    """更新班次类型信息"""
    db_shift_type = shift_type_service.update_shift_type(
        db, shift_type_id=shift_type_id, shift_type=shift_type
    )
    if db_shift_type is None:
        raise HTTPException(status_code=404, detail="班次类型不存在")
    return db_shift_type

@router.delete("/{shift_type_id}", response_model=shift_type_schema.ShiftType)
def delete_shift_type(shift_type_id: int, db: Session = Depends(get_db)):
    """删除班次类型"""
    db_shift_type = shift_type_service.delete_shift_type(db, shift_type_id=shift_type_id)
    if db_shift_type is None:
        raise HTTPException(status_code=404, detail="班次类型不存在")
    return db_shift_type

@router.get("/active/list", response_model=List[shift_type_schema.ShiftType])
def get_active_shift_types(db: Session = Depends(get_db)):
    """获取所有可用的班次类型（用于下拉选择）"""
    return shift_type_service.get_active_shift_types(db)

@router.post("/batch", response_model=List[shift_type_schema.ShiftType])
def create_batch_shift_types(
    shift_types: List[shift_type_schema.ShiftTypeCreate], 
    db: Session = Depends(get_db)
):
    """批量创建班次类型"""
    return shift_type_service.create_batch_shift_types(db=db, shift_types=shift_types)

@router.get("/validate/time-conflict")
def validate_time_conflict(
    start_time: str,
    end_time: str,
    shift_type_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """验证班次时间是否与现有班次类型冲突"""
    from datetime import time
    try:
        start_time_obj = time.fromisoformat(start_time)
        end_time_obj = time.fromisoformat(end_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="时间格式错误，请使用HH:MM:SS格式")
    
    conflict = shift_type_service.check_time_conflict(
        db, start_time_obj, end_time_obj, exclude_id=shift_type_id
    )
    return {"has_conflict": conflict is not None, "conflict_shift_type": conflict}