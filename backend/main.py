from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import engine, SessionLocal, Base
from api import auth, employees, attendance, schedules, shift_templates, shift_types, holidays, overtime_rules, compensatory_time_rules, exception_rules, reports, dashboard, notifications, warnings, my
from middleware.rate_limiting import RateLimitingMiddleware
from services import employee_service
from schemas.employee import EmployeeCreate
from datetime import date

# 导入所有模型以确保表结构被正确识别
from models import (
    employee, attendance_record, schedule, shift_template, 
    shift_type, holiday, overtime_rule, compensatory_time_rule, 
    exception_rule, notification, sync_log
)
from models import warnings as warnings_model

# 创建数据库表
Base.metadata.create_all(bind=engine)

def create_initial_admin():
    db = SessionLocal()
    try:
        admin_user = employee_service.get_employee_by_employee_no(db, "admin")
        if not admin_user:
            admin_employee = EmployeeCreate(
                employee_no="admin",
                name="系统管理员",
                password="admin123",
                gender="M",
                phone="13800138000",
                email="admin@company.com",
                position="系统管理员",
                hire_date=date.today(),
                is_admin=True
            )
            employee_service.create_employee(db, admin_employee)
            print("初始管理员账户创建成功")
    finally:
        db.close()

# 创建初始管理员
create_initial_admin()

app = FastAPI(title="员工考勤管理系统", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加限流中间件
app.add_middleware(RateLimitingMiddleware)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(employees.router, prefix="/api/employees", tags=["员工管理"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["考勤管理"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["排班管理"])
app.include_router(shift_templates.router, prefix="/api/shift_templates", tags=["班次模板"])
app.include_router(shift_types.router, prefix="/api/shift_types", tags=["班次类型"])
app.include_router(holidays.router, prefix="/api/holidays", tags=["节假日管理"])
app.include_router(overtime_rules.router, prefix="/api/overtime-rules", tags=["加班规则"])
app.include_router(compensatory_time_rules.router, prefix="/api/compensatory-time-rules", tags=["调休规则"])
app.include_router(exception_rules.router, prefix="/api/exception-rules", tags=["异常规则"])
app.include_router(reports.router, prefix="/api/reports", tags=["报表管理"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表盘"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["通知管理"])
app.include_router(warnings.router, prefix="/api/warnings", tags=["预警管理"])
app.include_router(my.router, prefix="/api/my", tags=["个人中心"])

@app.get("/")
def read_root():
    return {"message": "员工考勤管理系统 API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)