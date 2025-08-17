from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from api.auth import get_current_active_user
from models import employee as employee_model
from schemas import employee as employee_schema
from services import employee_service

router = APIRouter()

@router.get("/profile", response_model=dict)
async def get_my_profile(current_user: employee_model.Employee = Depends(get_current_active_user)):
    """获取当前用户的个人信息"""
    return {
        "id": current_user.employee_id,
        "employee_id": current_user.employee_id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "department": current_user.department.name if current_user.department else None,
        "position": current_user.position,
        "hireDate": current_user.hire_date.strftime("%Y-%m-%d") if current_user.hire_date else None,
        "hire_date": current_user.hire_date.strftime("%Y-%m-%d") if current_user.hire_date else None
    }

@router.put("/profile", response_model=dict)
async def update_my_profile(
    profile_data: employee_schema.EmployeeUpdate,
    current_user: employee_model.Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新当前用户的个人信息"""
    updated_employee = employee_service.update_employee(db, current_user.employee_id, profile_data)
    if not updated_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {
        "id": updated_employee.employee_id,
        "name": updated_employee.name,
        "email": updated_employee.email,
        "phone": updated_employee.phone,
        "department": updated_employee.department.name if updated_employee.department else None,
        "position": updated_employee.position,
        "hireDate": updated_employee.hire_date.strftime('%Y-%m-%d') if updated_employee.hire_date else None
    }

@router.post("/change-password")
async def change_password(
    password_data: dict,
    current_user: employee_model.Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """修改当前用户密码"""
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Current password and new password are required")
    
    # 验证当前密码
    from utils.security import verify_password
    if not verify_password(current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # 更新密码
    employee_service.update_employee_password(db, current_user.employee_id, new_password)
    
    return {"message": "Password updated successfully"}