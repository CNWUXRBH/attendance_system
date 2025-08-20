from sqlalchemy.orm import Session
from sqlalchemy import func, and_, distinct
from datetime import datetime, timedelta
from services import employee_service
from models.attendance_record import AttendanceRecord
from models.employee import Employee

def get_dashboard_stats(db: Session, date: str = None):
    # 解析日期参数
    target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else datetime.now().date()
    
    # 基础查询条件
    employee_query = db.query(Employee).filter(Employee.is_active == True)
    
    # 获取总员工数
    total_employees = employee_query.count()
    
    # 获取指定日期出勤人数（去重）- 只统计有打卡记录的员工
    present_today = db.query(distinct(AttendanceRecord.employee_id)).filter(
        func.date(AttendanceRecord.clock_in_time) == target_date
    )
    present_today = present_today.count()
    
    # 计算出勤率
    attendance_rate = round((present_today / total_employees * 100), 1) if total_employees > 0 else 0
    
    # 获取异常考勤数（指定日期迟到、早退等）
    abnormal_query = db.query(AttendanceRecord).filter(
        and_(
            func.date(AttendanceRecord.clock_in_time) == target_date,
            AttendanceRecord.status.in_(['迟到', '早退', '缺勤', '缺卡'])
        )
    )
    abnormal_attendance = abnormal_query.count()
    
    # 待处理请求数（这里暂时设为0，实际应该查询补卡申请等）
    pending_requests = 0
    
    # 获取过去7天的出勤统计
    weekly_attendance = []
    for i in range(7):
        date_item = target_date - timedelta(days=6-i)
        count_query = db.query(distinct(AttendanceRecord.employee_id)).filter(
            func.date(AttendanceRecord.clock_in_time) == date_item
        )
        count = count_query.count()
        weekly_attendance.append(count)
    
    return {
        "total_employees": total_employees,
        "present_today": present_today,
        "attendance_rate": attendance_rate,
        "abnormal_attendance": abnormal_attendance,
        "pending_requests": pending_requests,
        "weekly_attendance": weekly_attendance
    }