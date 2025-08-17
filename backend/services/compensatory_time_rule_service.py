from sqlalchemy.orm import Session
from typing import List, Optional

from models import compensatory_time_rule as compensatory_time_rule_model
from schemas import compensatory_time_rule as compensatory_time_rule_schema

def create_compensatory_time_rule(db: Session, rule: compensatory_time_rule_schema.CompensatoryTimeRuleCreate):
    db_rule = compensatory_time_rule_model.CompensatoryTimeRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def get_compensatory_time_rules(db: Session, skip: int = 0, limit: int = 100):
    return db.query(compensatory_time_rule_model.CompensatoryTimeRule).offset(skip).limit(limit).all()

def get_compensatory_time_rule(db: Session, rule_id: int):
    return db.query(compensatory_time_rule_model.CompensatoryTimeRule).filter(compensatory_time_rule_model.CompensatoryTimeRule.rule_id == rule_id).first()

def update_compensatory_time_rule(db: Session, rule_id: int, rule: compensatory_time_rule_schema.CompensatoryTimeRuleCreate):
    db_rule = get_compensatory_time_rule(db, rule_id)
    if db_rule:
        for key, value in rule.dict().items():
            setattr(db_rule, key, value)
        db.commit()
        db.refresh(db_rule)
    return db_rule

def delete_compensatory_time_rule(db: Session, rule_id: int):
    db_rule = get_compensatory_time_rule(db, rule_id)
    if db_rule:
        db.delete(db_rule)
        db.commit()
    return db_rule