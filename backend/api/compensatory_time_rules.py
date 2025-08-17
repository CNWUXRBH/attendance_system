from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas import compensatory_time_rule as compensatory_time_rule_schema
from services import compensatory_time_rule_service

router = APIRouter()

@router.post("/", response_model=compensatory_time_rule_schema.CompensatoryTimeRule)
def create_compensatory_time_rule(rule: compensatory_time_rule_schema.CompensatoryTimeRuleCreate, db: Session = Depends(get_db)):
    return compensatory_time_rule_service.create_compensatory_time_rule(db=db, rule=rule)

@router.get("/", response_model=List[compensatory_time_rule_schema.CompensatoryTimeRule])
def read_compensatory_time_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rules = compensatory_time_rule_service.get_compensatory_time_rules(db, skip=skip, limit=limit)
    return rules

@router.get("/{rule_id}", response_model=compensatory_time_rule_schema.CompensatoryTimeRule)
def read_compensatory_time_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = compensatory_time_rule_service.get_compensatory_time_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Compensatory time rule not found")
    return db_rule

@router.put("/{rule_id}", response_model=compensatory_time_rule_schema.CompensatoryTimeRule)
def update_compensatory_time_rule(rule_id: int, rule: compensatory_time_rule_schema.CompensatoryTimeRuleCreate, db: Session = Depends(get_db)):
    db_rule = compensatory_time_rule_service.update_compensatory_time_rule(db, rule_id=rule_id, rule=rule)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Compensatory time rule not found")
    return db_rule

@router.delete("/{rule_id}", response_model=compensatory_time_rule_schema.CompensatoryTimeRule)
def delete_compensatory_time_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = compensatory_time_rule_service.delete_compensatory_time_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Compensatory time rule not found")
    return db_rule