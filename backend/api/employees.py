from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import StreamingResponse

from database.database import get_db
from schemas import employee as employee_schema
from services import employee_service

router = APIRouter()

@router.post("/", response_model=employee_schema.Employee)
def create_employee(employee: employee_schema.EmployeeCreate, db: Session = Depends(get_db)):
    return employee_service.create_employee(db=db, employee=employee)

@router.get("/export")
def export_employees(db: Session = Depends(get_db)):
    output = employee_service.export_employees_to_excel(db)
    if output is None:
        raise HTTPException(status_code=404, detail="No employees to export.")
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=employees.xlsx"}
    )

@router.get("/", response_model=List[employee_schema.Employee])
def read_employees(skip: int = 0, limit: int = 100, name: str = None, db: Session = Depends(get_db)):
    employees = employee_service.get_employees(db, skip=skip, limit=limit, name=name)
    return employees

@router.get("/{employee_id}", response_model=employee_schema.Employee)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = employee_service.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.put("/{employee_id}", response_model=employee_schema.Employee)
def update_employee(employee_id: int, employee: employee_schema.EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = employee_service.update_employee(db, employee_id=employee_id, employee=employee)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.delete("/{employee_id}", response_model=employee_schema.Employee)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = employee_service.delete_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.post("/import")
async def import_employees(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file.")
    
    contents = await file.read()
    count = employee_service.import_employees_from_file(db, contents)
    
    return {"message": f"{count} employees imported successfully."}