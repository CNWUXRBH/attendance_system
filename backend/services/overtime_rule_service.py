from sqlalchemy.orm import Session
from typing import List, Optional

from models import overtime_rule as overtime_rule_model
from schemas import overtime_rule as overtime_rule_schema

def create_overtime_rule(db: Session, rule: overtime_rule_schema.OvertimeRuleCreate):
    db_rule = overtime_rule_model.OvertimeRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def get_overtime_rules(db: Session, skip: int = 0, limit: int = 100):
    return db.query(overtime_rule_model.OvertimeRule).offset(skip).limit(limit).all()

def get_overtime_rule(db: Session, rule_id: int):
    return db.query(overtime_rule_model.OvertimeRule).filter(overtime_rule_model.OvertimeRule.rule_id == rule_id).first()

def update_overtime_rule(db: Session, rule_id: int, rule: overtime_rule_schema.OvertimeRuleCreate):
    db_rule = get_overtime_rule(db, rule_id)
    if db_rule:
        for key, value in rule.dict().items():
            setattr(db_rule, key, value)
        db.commit()
        db.refresh(db_rule)
    return db_rule

def delete_overtime_rule(db: Session, rule_id: int):
    db_rule = get_overtime_rule(db, rule_id)
    if db_rule:
        db.delete(db_rule)
        db.commit()
    return db_rule