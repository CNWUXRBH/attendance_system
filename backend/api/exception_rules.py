from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas import exception_rule as exception_rule_schema
from services import exception_rule_service

router = APIRouter()

@router.post("/", response_model=exception_rule_schema.ExceptionRule)
def create_exception_rule(rule: exception_rule_schema.ExceptionRuleCreate, db: Session = Depends(get_db)):
    return exception_rule_service.create_exception_rule(db=db, rule=rule)

@router.get("/", response_model=List[exception_rule_schema.ExceptionRule])
def read_exception_rules(skip: int = 0, limit: int = 100, rule_name: str = None, db: Session = Depends(get_db)):
    rules = exception_rule_service.get_exception_rules(db, skip=skip, limit=limit, rule_name=rule_name)
    return rules

@router.get("/{rule_id}", response_model=exception_rule_schema.ExceptionRule)
def read_exception_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = exception_rule_service.get_exception_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return db_rule

@router.put("/{rule_id}", response_model=exception_rule_schema.ExceptionRule)
def update_exception_rule(rule_id: int, rule: exception_rule_schema.ExceptionRuleCreate, db: Session = Depends(get_db)):
    db_rule = exception_rule_service.update_exception_rule(db, rule_id=rule_id, rule=rule)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return db_rule

@router.delete("/{rule_id}", response_model=exception_rule_schema.ExceptionRule)
def delete_exception_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = exception_rule_service.delete_exception_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return db_rule

@router.get("/types/available")
def get_available_rule_types():
    """
    获取可用的规则类型
    
    Returns:
        可用的规则类型列表
    """
    return {
        "status": "success",
        "rule_types": [
            {
                "value": "迟到",
                "label": "迟到",
                "description": "检测员工上班迟到情况",
                "requires_threshold": True,
                "threshold_unit": "分钟"
            },
            {
                "value": "早退",
                "label": "早退",
                "description": "检测员工下班早退情况",
                "requires_threshold": True,
                "threshold_unit": "分钟"
            },
            {
                "value": "缺卡",
                "label": "缺卡",
                "description": "检测员工打卡缺失情况",
                "requires_threshold": False,
                "threshold_unit": None
            },
            {
                "value": "超期记录",
                "label": "超期记录",
                "description": "检测考勤记录或排班超出7天的情况",
                "requires_threshold": False,
                "threshold_unit": None
            }
        ]
    }