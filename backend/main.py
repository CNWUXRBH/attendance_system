from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.database import engine, SessionLocal, Base
from api import auth, employees, attendance, reports, dashboard, my
from middleware.rate_limiting import RateLimitingMiddleware
from services import employee_service
from services.mssql_sync_service import mssql_sync_service
from schemas.employee import EmployeeCreate
from datetime import date
import asyncio
import logging

# 导入所有模型以确保表结构被正确识别
from models import (
    employee, attendance_record, sync_log
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

def create_initial_admin():
    db = SessionLocal()
    try:
        # 优先按管理员账号 employee_no="admin" 检查
        admin_user = employee_service.get_employee_by_employee_no(db, "admin")
        if admin_user:
            # 确保拥有管理员权限
            if not admin_user.is_admin:
                admin_user.is_admin = True
                db.commit()
            print("管理员账户已存在，跳过创建")
            return

        # 若不存在admin账号，但已有相同邮箱用户，则复用该用户并升级为管理员
        existing_by_email = db.query(employee.Employee).filter(
            employee.Employee.email == "admin@company.com"
        ).first()
        if existing_by_email:
            existing_by_email.employee_no = "admin"
            existing_by_email.is_admin = True
            db.commit()
            # 重置密码为默认管理员密码
            employee_service.update_employee_password(db, existing_by_email.employee_id, "admin123")
            print("已将现有邮箱 admin@company.com 的用户升级为管理员并设置账号为 admin")
            return

        # 两者都不存在时，新建管理员
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
    except Exception as e:
        db.rollback()
        print(f"初始化管理员失败: {str(e)}")
    finally:
        db.close()

# 创建初始管理员
create_initial_admin()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的事件处理
    logger.info("正在启动后台同步服务...")
    # 使用默认的环境配置，不传递sync_interval_minutes参数
    mssql_sync_service.start_background_sync()
    logger.info("后台同步服务启动完成")
    
    yield
    
    # 关闭时的事件处理
    logger.info("正在停止后台同步服务...")
    mssql_sync_service.stop_background_sync()
    logger.info("后台同步服务已停止")

app = FastAPI(title="员工考勤管理系统", version="1.0.0", lifespan=lifespan)

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
app.include_router(reports.router, prefix="/api/reports", tags=["报表管理"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表盘"])

app.include_router(my.router, prefix="/api/my", tags=["个人中心"])

@app.get("/")
def read_root():
    return {"message": "员工考勤管理系统 API"}

@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "healthy", "message": "服务运行正常"}

@app.get("/api/sync-status")
def get_sync_status():
    """获取同步服务状态"""
    return mssql_sync_service.get_background_sync_status()

@app.post("/api/sync-control")
def control_sync_service(action: str, sync_interval_minutes: int = None):
    """控制同步服务
    
    Args:
        action: 操作类型 (start/stop/restart)
        sync_interval_minutes: 同步间隔（分钟），仅在start/restart时有效
    """
    try:
        if action == "start":
            interval = sync_interval_minutes or 5
            mssql_sync_service.start_background_sync(sync_interval_minutes=interval)
            return {"success": True, "message": f"同步服务已启动，间隔: {interval}分钟"}
        elif action == "stop":
            mssql_sync_service.stop_background_sync()
            return {"success": True, "message": "同步服务已停止"}
        elif action == "restart":
            mssql_sync_service.stop_background_sync()
            interval = sync_interval_minutes or 5
            mssql_sync_service.start_background_sync(sync_interval_minutes=interval)
            return {"success": True, "message": f"同步服务已重启，间隔: {interval}分钟"}
        else:
            return {"success": False, "message": "无效的操作类型，支持: start/stop/restart"}
    except Exception as e:
        return {"success": False, "message": f"操作失败: {str(e)}"}

@app.post("/api/sync-trigger")
def trigger_manual_sync():
    """手动触发一次同步（不影响定时同步）"""
    try:
        # 这里可以添加手动触发同步的逻辑
        # 暂时返回提示信息
        return {
            "success": True, 
            "message": "手动同步功能暂未实现，系统正在使用自动增量同步"
        }
    except Exception as e:
        return {"success": False, "message": f"手动同步失败: {str(e)}"}

@app.get("/api/sync-metrics")
def get_sync_metrics():
    """获取同步监控指标"""
    try:
        return {
            "success": True,
            "data": mssql_sync_service.get_sync_metrics()
        }
    except Exception as e:
        return {"success": False, "message": f"获取监控指标失败: {str(e)}"}

@app.get("/api/sync-health")
def get_sync_health():
    """获取同步服务健康状态"""
    try:
        status = mssql_sync_service.get_background_sync_status()
        return {
            "success": True,
            "health_status": status.get("health_status", {}),
            "is_running": status.get("is_running", False),
            "last_sync_time": status.get("last_sync_time"),
            "sync_status": status.get("sync_status", "unknown")
        }
    except Exception as e:
        return {"success": False, "message": f"获取健康状态失败: {str(e)}"}

@app.post("/api/sync-interval")
def update_sync_interval(interval_minutes: int):
    """动态更新同步间隔"""
    try:
        if interval_minutes < 1:
            return {"success": False, "message": "同步间隔不能小于1分钟"}
        
        result = mssql_sync_service.update_sync_interval(interval_minutes)
        
        # 如果服务正在运行，提示需要重启
        if result.get('requires_restart'):
            result['restart_tip'] = "同步服务正在运行，新的间隔将在下次重启后生效。可以调用 /api/sync-control 重启服务。"
        
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "message": f"更新同步间隔失败: {str(e)}"}

@app.get("/api/sync-config")
def get_sync_config():
    """获取当前同步配置信息"""
    try:
        status = mssql_sync_service.get_background_sync_status()
        env_name = mssql_sync_service._get_environment_name()
        
        return {
            "success": True,
            "config": {
                "environment": env_name,
                "sync_interval_minutes": status.get('sync_interval_minutes'),
                "is_running": status.get('is_running'),
                "status": status.get('status'),
                "last_sync_time": status.get('last_sync_time'),
                "thread_alive": status.get('thread_alive')
            }
        }
    except Exception as e:
        return {"success": False, "message": f"获取同步配置失败: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)