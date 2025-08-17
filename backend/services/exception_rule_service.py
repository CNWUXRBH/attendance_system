from sqlalchemy.orm import Session
from typing import List, Optional

from models import exception_rule as exception_rule_model
from schemas import exception_rule as exception_rule_schema

def create_exception_rule(db: Session, rule: exception_rule_schema.ExceptionRuleCreate):
    db_rule = exception_rule_model.ExceptionRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def get_exception_rules(db: Session, skip: int = 0, limit: int = 100, rule_name: Optional[str] = None):
    query = db.query(exception_rule_model.ExceptionRule)
    if rule_name:
        query = query.filter(exception_rule_model.ExceptionRule.rule_name.contains(rule_name))
    rules = query.offset(skip).limit(limit).all()
    return rules

def get_exception_rule(db: Session, rule_id: int):
    return db.query(exception_rule_model.ExceptionRule).filter(exception_rule_model.ExceptionRule.rule_id == rule_id).first()

def update_exception_rule(db: Session, rule_id: int, rule: exception_rule_schema.ExceptionRuleCreate):
    db_rule = get_exception_rule(db, rule_id)
    if db_rule:
        for key, value in rule.dict().items():
            setattr(db_rule, key, value)
        db.commit()
        db.refresh(db_rule)
    return db_rule

def delete_exception_rule(db: Session, rule_id: int):
    db_rule = get_exception_rule(db, rule_id)
    if db_rule:
        db.delete(db_rule)
        db.commit()
    return db_rule