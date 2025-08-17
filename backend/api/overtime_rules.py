from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas import overtime_rule as overtime_rule_schema
from services import overtime_rule_service

router = APIRouter()

@router.post("/", response_model=overtime_rule_schema.OvertimeRule)
def create_overtime_rule(rule: overtime_rule_schema.OvertimeRuleCreate, db: Session = Depends(get_db)):
    return overtime_rule_service.create_overtime_rule(db=db, rule=rule)

@router.get("/", response_model=List[overtime_rule_schema.OvertimeRule])
def read_overtime_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rules = overtime_rule_service.get_overtime_rules(db, skip=skip, limit=limit)
    return rules

@router.get("/{rule_id}", response_model=overtime_rule_schema.OvertimeRule)
def read_overtime_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = overtime_rule_service.get_overtime_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Overtime rule not found")
    return db_rule

@router.put("/{rule_id}", response_model=overtime_rule_schema.OvertimeRule)
def update_overtime_rule(rule_id: int, rule: overtime_rule_schema.OvertimeRuleCreate, db: Session = Depends(get_db)):
    db_rule = overtime_rule_service.update_overtime_rule(db, rule_id=rule_id, rule=rule)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Overtime rule not found")
    return db_rule

@router.delete("/{rule_id}", response_model=overtime_rule_schema.OvertimeRule)
def delete_overtime_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = overtime_rule_service.delete_overtime_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Overtime rule not found")
    return db_rule