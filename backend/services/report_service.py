from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO

from models import attendance_record as models_ar, employee as models_e

def _calculate_work_details(record, db):
    """
    简化的工作时长计算，不依赖排班信息
    """
    if not record.clock_in_time or not record.clock_out_time:
        return None, None, None, None

    # 计算实际工作时长
    work_duration = record.clock_out_time - record.clock_in_time
    
    # 假设标准工作时长为8小时
    standard_work_duration = timedelta(hours=8)
    
    # 计算加班时长（超过8小时的部分）
    overtime = work_duration - standard_work_duration if work_duration > standard_work_duration else timedelta(0)
    
    # 简单的状态判断（基于记录中的状态字段，如果没有则默认为正常）
    status = record.status if record.status else "正常"
    
    # 返回工作时长、加班时长、状态和班次名称（固定为"标准班次"）
    return work_duration, overtime, status, "标准班次"

def get_detailed_report_data(db: Session, start_date: datetime.date, end_date: datetime.date):
    """
    获取详细报表数据，简化版本不依赖排班信息
    """
    records = db.query(models_ar.AttendanceRecord).filter(
        func.date(models_ar.AttendanceRecord.clock_in_time) >= start_date,
        func.date(models_ar.AttendanceRecord.clock_in_time) <= end_date
    ).all()

    if not records:
        return []

    employee_ids = {r.employee_id for r in records}
    employees = db.query(models_e.Employee).filter(models_e.Employee.employee_id.in_(employee_ids)).all()
    employee_map = {e.employee_id: e for e in employees}

    report_data = []
    for record in records:
        employee = employee_map.get(record.employee_id)
        
        # 使用简化的工作时长计算
        work_duration, overtime, status, shift_name = _calculate_work_details(record, db)

        report_data.append({
            "employee_name": employee.name if employee else "N/A",
            "clock_in_time": record.clock_in_time,
            "clock_out_time": record.clock_out_time,
            "work_duration": str(work_duration) if work_duration else "N/A",
            "overtime": str(overtime) if overtime else "N/A",
            "status": status if status else "N/A",
            "shift_name": shift_name if shift_name else "N/A"
        })
    return report_data

def export_detailed_report_to_excel(report_data):
    if not report_data:
        return None

    df = pd.DataFrame(report_data)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Detailed Report')
    writer.close()
    output.seek(0)
    return output

def get_reports(db: Session):
    """获取报表列表 - 基于真实数据库数据"""
    from datetime import datetime, timedelta
    
    # 获取最近30天的考勤记录统计
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    # 统计总考勤记录数
    total_records = db.query(models_ar.AttendanceRecord).filter(
        func.date(models_ar.AttendanceRecord.clock_in_time) >= start_date,
        func.date(models_ar.AttendanceRecord.clock_in_time) <= end_date
    ).count()
    
    # 统计异常考勤记录数（迟到、早退等）
    abnormal_records = db.query(models_ar.AttendanceRecord).filter(
        func.date(models_ar.AttendanceRecord.clock_in_time) >= start_date,
        func.date(models_ar.AttendanceRecord.clock_in_time) <= end_date,
        models_ar.AttendanceRecord.status.in_(['迟到', '早退', '缺勤'])
    ).count()
    
    # 统计员工总数
    total_employees = db.query(models_e.Employee).count()
    
    # 获取最新的考勤记录时间
    latest_record = db.query(models_ar.AttendanceRecord).order_by(
        models_ar.AttendanceRecord.clock_in_time.desc()
    ).first()
    
    latest_time = latest_record.clock_in_time.isoformat() if latest_record else datetime.now().isoformat()
    
    return {
        "reports": [
            {
                "id": 1,
                "name": f"月度考勤报表 (共{total_records}条记录)",
                "type": "monthly",
                "created_at": latest_time,
                "status": "completed",
                "total_records": total_records,
                "total_employees": total_employees
            },
            {
                "id": 2,
                "name": f"异常考勤统计 (共{abnormal_records}条异常)",
                "type": "exception",
                "created_at": latest_time,
                "status": "completed",
                "abnormal_count": abnormal_records
            },

        ]
    }

def generate_report(db: Session, report_type: str, start_date: str = None, end_date: str = None):
    """生成报表 - 基于真实数据库数据"""
    from datetime import datetime, timedelta
    import uuid
    
    # 设置默认日期范围
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return {
            "success": False,
            "message": "日期格式错误，请使用YYYY-MM-DD格式",
            "report_id": None,
            "download_url": None
        }
    
    # 根据报表类型获取真实数据
    if report_type == "monthly":
        # 获取月度考勤数据
        records = db.query(models_ar.AttendanceRecord).filter(
            func.date(models_ar.AttendanceRecord.clock_in_time) >= start_dt,
            func.date(models_ar.AttendanceRecord.clock_in_time) <= end_dt
        ).count()
        
        report_data = get_detailed_report_data(db, start_dt, end_dt)
        
    elif report_type == "exception":
        # 获取异常考勤数据
        records = db.query(models_ar.AttendanceRecord).filter(
            func.date(models_ar.AttendanceRecord.clock_in_time) >= start_dt,
            func.date(models_ar.AttendanceRecord.clock_in_time) <= end_dt,
            models_ar.AttendanceRecord.status.in_(['迟到', '早退', '缺勤'])
        ).count()
        
        report_data = get_detailed_report_data(db, start_dt, end_dt)
        # 过滤只保留异常记录
        report_data = [r for r in report_data if r['status'] in ['迟到', '早退', '缺勤']]
        

    else:
        return {
            "success": False,
            "message": f"不支持的报表类型: {report_type}",
            "report_id": None,
            "download_url": None
        }
    
    # 生成唯一的报表ID
    report_id = str(uuid.uuid4())[:8]
    
    return {
        "success": True,
        "message": f"报表生成成功: {report_type}，共{records}条数据",
        "report_id": report_id,
        "download_url": f"/api/reports/download/{report_id}",
        "data_count": records,
        "date_range": f"{start_date} 至 {end_date}",
        "report_data": report_data
    }
