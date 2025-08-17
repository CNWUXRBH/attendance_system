from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
from io import BytesIO
from datetime import date, datetime
import random
import logging

from models import attendance_record as attendance_record_model
from models import employee as employee_model
from schemas import attendance_record as attendance_record_schema
from services.exception_detection_service import exception_detection_service

logger = logging.getLogger(__name__)

def create_attendance_record(db: Session, record: attendance_record_schema.AttendanceRecordCreate):
    db_record = attendance_record_model.AttendanceRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # 创建记录后进行异常检测
    try:
        exceptions = exception_detection_service.detect_attendance_exceptions(db, record_id=db_record.record_id)
        exception_detection_service.update_record_status_based_on_exceptions(db, db_record.record_id, exceptions)
        logger.info(f"考勤记录 {db_record.record_id} 异常检测完成，发现 {len(exceptions)} 个异常")
    except Exception as e:
        logger.error(f"考勤记录 {db_record.record_id} 异常检测失败: {str(e)}")
    
    return db_record

def get_attendance_records(db: Session, skip: int = 0, limit: int = 100, employee_id: Optional[int] = None, start_date: Optional[date] = None, end_date: Optional[date] = None):
    query = db.query(attendance_record_model.AttendanceRecord)
    if employee_id:
        query = query.filter(attendance_record_model.AttendanceRecord.employee_id == employee_id)
    if start_date:
        query = query.filter(attendance_record_model.AttendanceRecord.clock_in_time >= start_date)
    if end_date:
        query = query.filter(attendance_record_model.AttendanceRecord.clock_in_time <= end_date)
    records = query.offset(skip).limit(limit).all()
    return records

def get_attendance_records_formatted(db: Session, skip: int = 0, limit: int = 100, employee_id: Optional[int] = None, start_date: Optional[date] = None, end_date: Optional[date] = None):
    query = db.query(
        attendance_record_model.AttendanceRecord,
        employee_model.Employee.name,
        employee_model.Employee.position
    ).join(
        employee_model.Employee,
        attendance_record_model.AttendanceRecord.employee_id == employee_model.Employee.employee_id
    )
    
    if employee_id:
        query = query.filter(attendance_record_model.AttendanceRecord.employee_id == employee_id)
    if start_date:
        query = query.filter(attendance_record_model.AttendanceRecord.clock_in_time >= start_date)
    if end_date:
        query = query.filter(attendance_record_model.AttendanceRecord.clock_in_time <= end_date)
    
    results = query.offset(skip).limit(limit).all()
    
    formatted_records = []
    for record, employee_name, position in results:
        formatted_record = {
            'record_id': record.record_id,
            'date': record.clock_in_time.strftime('%Y-%m-%d') if record.clock_in_time else '',
            'name': employee_name,
            'department': position,
            'checkIn': record.clock_in_time.strftime('%H:%M:%S') if record.clock_in_time else None,
            'checkOut': record.clock_out_time.strftime('%H:%M:%S') if record.clock_out_time else None,
            'status': record.status or '正常',
            'employee_id': record.employee_id,
            'clock_type': record.clock_type,
            'device_id': record.device_id,
            'location': record.location
        }
        formatted_records.append(formatted_record)
    
    return formatted_records

def get_attendance_record(db: Session, record_id: int):
    return db.query(attendance_record_model.AttendanceRecord).filter(attendance_record_model.AttendanceRecord.record_id == record_id).first()

def update_attendance_record(db: Session, record_id: int, record: attendance_record_schema.AttendanceRecordCreate):
    db_record = get_attendance_record(db, record_id)
    if db_record:
        for key, value in record.dict().items():
            setattr(db_record, key, value)
        db.commit()
        db.refresh(db_record)
        
        # 更新记录后重新进行异常检测
        try:
            exceptions = exception_detection_service.detect_attendance_exceptions(db, record_id=db_record.record_id)
            exception_detection_service.update_record_status_based_on_exceptions(db, db_record.record_id, exceptions)
            logger.info(f"考勤记录 {db_record.record_id} 更新后异常检测完成，发现 {len(exceptions)} 个异常")
        except Exception as e:
            logger.error(f"考勤记录 {db_record.record_id} 更新后异常检测失败: {str(e)}")
    
    return db_record

def delete_attendance_record(db: Session, record_id: int):
    db_record = get_attendance_record(db, record_id)
    if db_record:
        db.delete(db_record)
        db.commit()
    return db_record

def import_records_from_file(db: Session, contents: bytes):
    df = pd.read_excel(BytesIO(contents))
    for _, row in df.iterrows():
        if 'clock_in_time' in row and pd.notna(row['clock_in_time']):
            row['clock_in_time'] = pd.to_datetime(row['clock_in_time'])
        if 'clock_out_time' in row and pd.notna(row['clock_out_time']):
            row['clock_out_time'] = pd.to_datetime(row['clock_out_time'])
        record_data = attendance_record_schema.AttendanceRecordCreate(**row.to_dict())
        db_record = attendance_record_model.AttendanceRecord(**record_data.dict())
        db.add(db_record)
    db.commit()
    return len(df)

def export_records_to_excel(db: Session):
    records = db.query(attendance_record_model.AttendanceRecord).all()
    if not records:
        return None
    
    record_list = []
    for r in records:
        record_list.append({
            'record_id': r.record_id,
            'employee_id': r.employee_id,
            'clock_in_time': r.clock_in_time.strftime('%Y-%m-%d %H:%M:%S') if r.clock_in_time else None,
            'clock_out_time': r.clock_out_time.strftime('%Y-%m-%d %H:%M:%S') if r.clock_out_time else None,
            'clock_type': r.clock_type,
            'device_id': r.device_id,
            'location': r.location,
            'status': r.status,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else None,
            'updated_at': r.updated_at.strftime('%Y-%m-%d %H:%M:%S') if r.updated_at else None
        })

    df = pd.DataFrame(record_list)
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Attendance Records')
    writer.close()
    output.seek(0)
    
    return output

# 注意：模拟数据函数已移除，现在使用真实的MSSQL同步服务
# 请使用 mssql_sync_service.sync_attendance_records() 进行数据同步

def update_attendance_process_status(db: Session, record_id: int, process_status: str, remarks: str = None):
    """更新考勤记录的处理状态"""
    db_record = db.query(attendance_record_model.AttendanceRecord).filter(
        attendance_record_model.AttendanceRecord.record_id == record_id
    ).first()
    
    if db_record is None:
        return None
    
    # 更新处理状态和备注
    db_record.process_status = process_status
    if remarks is not None:
        db_record.remarks = remarks
    
    db.commit()
    db.refresh(db_record)
    return db_record