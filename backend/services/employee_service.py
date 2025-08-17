from sqlalchemy.orm import Session
from typing import List
import pandas as pd
from io import BytesIO

from models import employee as employee_model
from schemas import employee as employee_schema
from utils.security import get_password_hash, verify_password

def authenticate_user(db: Session, username: str, password: str):
    db_employee = db.query(employee_model.Employee).filter(employee_model.Employee.employee_no == username).first()
    if not db_employee:
        return False
    if not verify_password(password, db_employee.password):
        return False
    return db_employee

def create_employee(db: Session, employee: employee_schema.EmployeeCreate):
    hashed_password = get_password_hash(employee.password)
    db_employee = employee_model.Employee(
        **employee.dict(exclude={"password"}), 
        password=hashed_password
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def get_employees(db: Session, skip: int = 0, limit: int = 100, name: str = None):
    query = db.query(employee_model.Employee)
    if name:
        query = query.filter(employee_model.Employee.name.contains(name))
    employees = query.offset(skip).limit(limit).all()
    return employees

def get_employee(db: Session, employee_id: int):
    return db.query(employee_model.Employee).filter(employee_model.Employee.employee_id == employee_id).first()

def update_employee(db: Session, employee_id: int, employee: employee_schema.EmployeeCreate):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        update_data = employee.dict(exclude_unset=True)
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            db_employee.password = hashed_password
        for key, value in update_data.items():
            if key != "password":
                setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
    return db_employee

def delete_employee(db: Session, employee_id: int):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        db.delete(db_employee)
        db.commit()
    return db_employee

def get_employee_by_employee_no(db: Session, employee_no: str):
    return db.query(employee_model.Employee).filter(employee_model.Employee.employee_no == employee_no).first()

def import_employees_from_file(db: Session, contents: bytes):
    df = pd.read_excel(BytesIO(contents))
    
    for index, row in df.iterrows():
        employee_data = employee_schema.EmployeeCreate(**row.to_dict())
        # 对密码进行哈希处理
        hashed_password = get_password_hash(employee_data.password)
        db_employee = employee_model.Employee(
            **employee_data.dict(exclude={"password"}),
            password=hashed_password
        )
        db.add(db_employee)
    
    db.commit()
    return len(df)

def export_employees_to_excel(db: Session):
    try:
        employees = db.query(employee_model.Employee).all()
        print(f"Found {len(employees)} employees in database")
        
        if not employees:
            return None
            
        employee_list = []
        for e in employees:
            employee_dict = {
                'employee_id': e.employee_id,
                'employee_no': e.employee_no,
                'name': e.name,
                'gender': e.gender,
                'phone': e.phone,
                'email': e.email,
                'position': e.position,
                'hire_date': e.hire_date.strftime('%Y-%m-%d') if e.hire_date else None,
                'is_admin': e.is_admin
            }
            employee_list.append(employee_dict)
        
        print(f"Processed {len(employee_list)} employee records")
        df = pd.DataFrame(employee_list)
        
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Employees')
        writer.close()
        output.seek(0)
        
        print("Excel file created successfully")
        return output
    except Exception as e:
        print(f"Error in export_employees_to_excel: {str(e)}")
        raise e

def update_employee_password(db: Session, employee_id: int, new_password: str):
    """更新员工密码"""
    db_employee = get_employee(db, employee_id)
    if db_employee:
        hashed_password = get_password_hash(new_password)
        db_employee.password = hashed_password
        db.commit()
        db.refresh(db_employee)
    return db_employee