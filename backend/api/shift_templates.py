from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database.database import get_db
from schemas import shift_template as shift_template_schema
from services import shift_template_service

router = APIRouter()

@router.post("/", response_model=shift_template_schema.ShiftTemplate)
def create_shift_template(shift_template: shift_template_schema.ShiftTemplateCreate, db: Session = Depends(get_db)):
    return shift_template_service.create_shift_template(db=db, shift_template=shift_template)

@router.get("/", response_model=List[shift_template_schema.ShiftTemplate])
def read_shift_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    shift_templates = shift_template_service.get_shift_templates(db, skip=skip, limit=limit)
    return shift_templates

@router.get("/{shift_template_id}", response_model=shift_template_schema.ShiftTemplate)
def read_shift_template(shift_template_id: int, db: Session = Depends(get_db)):
    db_shift_template = shift_template_service.get_shift_template(db, shift_template_id=shift_template_id)
    if db_shift_template is None:
        raise HTTPException(status_code=404, detail="ShiftTemplate not found")
    return db_shift_template

@router.put("/{shift_template_id}", response_model=shift_template_schema.ShiftTemplate)
def update_shift_template(shift_template_id: int, shift_template: shift_template_schema.ShiftTemplateCreate, db: Session = Depends(get_db)):
    db_shift_template = shift_template_service.update_shift_template(db, shift_template_id=shift_template_id, shift_template=shift_template)
    if db_shift_template is None:
        raise HTTPException(status_code=404, detail="ShiftTemplate not found")
    return db_shift_template

@router.delete("/{shift_template_id}", response_model=shift_template_schema.ShiftTemplate)
def delete_shift_template(shift_template_id: int, db: Session = Depends(get_db)):
    db_shift_template = shift_template_service.delete_shift_template(db, shift_template_id=shift_template_id)
    if db_shift_template is None:
        raise HTTPException(status_code=404, detail="ShiftTemplate not found")
    return db_shift_template

@router.post("/apply")
def apply_template_to_schedules(
    apply_data: shift_template_schema.ShiftTemplateApply,
    db: Session = Depends(get_db)
):
    """应用排班模板到指定员工和日期范围"""
    return shift_template_service.apply_template_to_schedules(
        db=db,
        template_id=apply_data.template_id,
        employee_ids=apply_data.employee_ids,
        start_date=apply_data.start_date,
        end_date=apply_data.end_date
    )