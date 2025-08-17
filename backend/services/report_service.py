from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO

from models import attendance_record as models_ar, schedule as models_s, shift_template as models_st, employee as models_e

def _calculate_work_details(record, db):
    schedule = db.query(models_s.Schedule).filter(
        models_s.Schedule.employee_id == record.employee_id,
        func.date(record.clock_in_time) >= models_s.Schedule.start_date,
        func.date(record.clock_in_time) <= models_s.Schedule.end_date
    ).first()

    if not schedule or not record.clock_in_time or not record.clock_out_time:
        return None, None, None, None

    shift_template = db.query(models_st.ShiftTemplate).filter(models_st.ShiftTemplate.id == schedule.shift_type_id).first()
    if not shift_template:
        return None, None, None, None

    work_duration = record.clock_out_time - record.clock_in_time
    scheduled_work_duration = timedelta(hours=shift_template.end_time.hour - shift_template.start_time.hour, 
                                        minutes=shift_template.end_time.minute - shift_template.start_time.minute)
    
    overtime = work_duration - scheduled_work_duration if work_duration > scheduled_work_duration else timedelta(0)
    
    status = "正常"
    if record.clock_in_time.time() > shift_template.start_time:
        status = "迟到"
    if record.clock_out_time.time() < shift_template.end_time:
        status = "早退"

    return work_duration, overtime, status, shift_template.name

def get_detailed_report_data(db: Session, start_date: datetime.date, end_date: datetime.date):
    records = db.query(models_ar.AttendanceRecord).filter(
        func.date(models_ar.AttendanceRecord.clock_in_time) >= start_date,
        func.date(models_ar.AttendanceRecord.clock_in_time) <= end_date
    ).all()

    if not records:
        return []

    employee_ids = {r.employee_id for r in records}
    employees = db.query(models_e.Employee).filter(models_e.Employee.employee_id.in_(employee_ids)).all()
    employee_map = {e.employee_id: e for e in employees}

    schedules = db.query(models_s.Schedule).filter(
        models_s.Schedule.employee_id.in_(employee_ids),
        models_s.Schedule.start_date <= end_date,
        models_s.Schedule.end_date >= start_date
    ).all()
    schedule_map = {(s.employee_id, d.date()): s for s in schedules for d in pd.date_range(s.start_date, s.end_date)}

    shift_template_ids = {s.shift_type_id for s in schedules}
    shift_templates = db.query(models_st.ShiftTemplate).filter(models_st.ShiftTemplate.id.in_(shift_template_ids)).all()
    shift_template_map = {st.id: st for st in shift_templates}

    report_data = []
    for record in records:
        employee = employee_map.get(record.employee_id)
        schedule = schedule_map.get((record.employee_id, record.clock_in_time.date()))
        
        work_duration, overtime, status, shift_name = None, None, "未排班", None

        if schedule:
            shift_template = shift_template_map.get(schedule.shift_type_id)
            if shift_template:
                shift_name = shift_template.name
                if record.clock_in_time and record.clock_out_time:
                    work_duration = record.clock_out_time - record.clock_in_time
                    scheduled_work_duration = timedelta(hours=shift_template.end_time.hour - shift_template.start_time.hour, 
                                                        minutes=shift_template.end_time.minute - shift_template.start_time.minute)
                    
                    overtime = work_duration - scheduled_work_duration if work_duration > scheduled_work_duration else timedelta(0)
                    
                    status = "正常"
                    if record.clock_in_time.time() > shift_template.start_time:
                        status = "迟到"
                    if record.clock_out_time.time() < shift_template.end_time:
                        status = "早退"

        report_data.append({
            "employee_name": employee.name if employee else "N/A",
            "clock_in_time": record.clock_in_time,
            "clock_out_time": record.clock_out_time,
            "work_duration": str(work_duration) if work_duration else "N/A",
            "overtime": str(overtime) if overtime else "N/A",
            "status": status,
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
            {
                "id": 3,
                "name": "员工出勤率统计",
                "type": "attendance_rate",
                "created_at": latest_time,
                "status": "completed",
                "attendance_rate": round((total_records / max(total_employees * 30, 1)) * 100, 2) if total_employees > 0 else 0
            }
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
        
    elif report_type == "attendance_rate":
        # 获取出勤率数据
        total_employees = db.query(models_e.Employee).count()
        total_records = db.query(models_ar.AttendanceRecord).filter(
            func.date(models_ar.AttendanceRecord.clock_in_time) >= start_dt,
            func.date(models_ar.AttendanceRecord.clock_in_time) <= end_dt
        ).count()
        
        records = total_records
        report_data = {
            "total_employees": total_employees,
            "total_records": total_records,
            "attendance_rate": round((total_records / max(total_employees * (end_dt - start_dt).days, 1)) * 100, 2) if total_employees > 0 else 0
        }
        
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
        "report_data": report_data if report_type != "attendance_rate" else report_data
    }
