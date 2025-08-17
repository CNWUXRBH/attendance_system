from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from fastapi.responses import StreamingResponse

from database.database import get_db
from schemas import attendance_record as attendance_record_schema
from services import attendance_service
from services.exception_detection_service import exception_detection_service

router = APIRouter()

@router.post("/", response_model=attendance_record_schema.AttendanceRecord)
def create_attendance_record(record: attendance_record_schema.AttendanceRecordCreate, db: Session = Depends(get_db)):
    return attendance_service.create_attendance_record(db=db, record=record)

@router.get("/export")
def export_attendance_records(db: Session = Depends(get_db)):
    output = attendance_service.export_records_to_excel(db)
    if output is None:
        raise HTTPException(status_code=404, detail="No attendance records to export.")
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=attendance_records.xlsx"}
    )

@router.get("/", response_model=List[attendance_record_schema.AttendanceRecordResponse])
def read_attendance_records(
    skip: int = 0,
    limit: int = 100,
    employee_id: int = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    records = attendance_service.get_attendance_records_formatted(db, skip=skip, limit=limit, employee_id=employee_id, start_date=start_date, end_date=end_date)
    return records

@router.get("/{record_id}", response_model=attendance_record_schema.AttendanceRecord)
def read_attendance_record(record_id: int, db: Session = Depends(get_db)):
    db_record = attendance_service.get_attendance_record(db, record_id=record_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return db_record

@router.put("/{record_id}", response_model=attendance_record_schema.AttendanceRecord)
def update_attendance_record(record_id: int, record: attendance_record_schema.AttendanceRecordCreate, db: Session = Depends(get_db)):
    db_record = attendance_service.update_attendance_record(db, record_id=record_id, record=record)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return db_record

@router.delete("/{record_id}", response_model=attendance_record_schema.AttendanceRecord)
def delete_attendance_record(record_id: int, db: Session = Depends(get_db)):
    db_record = attendance_service.delete_attendance_record(db, record_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return db_record

@router.patch("/{record_id}/process-status")
def update_attendance_process_status(
    record_id: int, 
    process_status: str,
    remarks: str = None,
    db: Session = Depends(get_db)
):
    """更新考勤记录的处理状态"""
    try:
        db_record = attendance_service.update_attendance_process_status(
            db, record_id, process_status, remarks
        )
        if db_record is None:
            raise HTTPException(status_code=404, detail="考勤记录未找到")
        return {"message": "处理状态更新成功", "record_id": record_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")

@router.post("/import")
async def import_attendance_records(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file.")
    
    contents = await file.read()
    count = attendance_service.import_records_from_file(db, contents)
    
    return {"message": f"{count} attendance records imported successfully."}

@router.post("/sync-external")
def sync_from_external_system(
    sync_date: str = None,
    employee_nos: str = None,
    db: Session = Depends(get_db)
):
    """
    从MSSQL外部系统同步考勤数据
    
    Args:
        sync_date: 同步日期，格式：YYYY-MM-DD，默认为今天
        employee_nos: 员工工号列表，用逗号分隔，为空则同步所有员工
    """
    try:
        from services.mssql_sync_service import mssql_sync_service
        
        # 解析员工工号列表
        employee_no_list = None
        if employee_nos:
            employee_no_list = [no.strip() for no in employee_nos.split(',') if no.strip()]
        
        # 执行同步
        result = mssql_sync_service.sync_attendance_records(
            db=db,
            sync_date=sync_date,
            employee_nos=employee_no_list
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")

@router.get("/sync-logs")
def get_sync_logs(limit: int = 50, db: Session = Depends(get_db)):
    """
    获取同步日志列表
    """
    try:
        from services.mssql_sync_service import mssql_sync_service
        logs = mssql_sync_service.get_sync_logs(db, limit)
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "sync_type": log.sync_type,
                    "sync_source": log.sync_source,
                    "sync_date": log.sync_date,
                    "employee_no": log.employee_no,
                    "sync_status": log.sync_status,
                    "records_count": log.records_count,
                    "error_message": log.error_message,
                    "sync_start_time": log.sync_start_time.isoformat() if log.sync_start_time else None,
                    "sync_end_time": log.sync_end_time.isoformat() if log.sync_end_time else None,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in logs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取同步日志失败: {str(e)}")

@router.get("/test-mssql-connection")
def test_mssql_connection():
    """
    测试MSSQL数据库连接
    """
    try:
        from services.mssql_sync_service import mssql_sync_service
        is_connected = mssql_sync_service.test_mssql_connection()
        
        return {
            "connected": is_connected,
            "message": "MSSQL连接正常" if is_connected else "MSSQL连接失败"
        }
    except Exception as e:
        return {
            "connected": False,
            "message": f"MSSQL连接测试失败: {str(e)}"
        }

@router.post("/detect-exceptions")
def detect_attendance_exceptions(
    record_id: int = None,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """
    检测考勤异常
    
    Args:
        record_id: 指定记录ID，如果提供则只检测该记录
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        db: 数据库会话
        
    Returns:
        检测到的异常列表
    """
    try:
        exceptions = exception_detection_service.detect_attendance_exceptions(
            db=db,
            record_id=record_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "status": "success",
            "message": f"异常检测完成，共发现 {len(exceptions)} 个异常",
            "exceptions": exceptions,
            "total_count": len(exceptions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"异常检测失败: {str(e)}")

@router.post("/batch-detect-exceptions")
def batch_detect_and_update_exceptions(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """
    批量检测异常并更新记录状态
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        db: 数据库会话
        
    Returns:
        批量处理结果
    """
    try:
        # 获取需要检测的记录
        records = attendance_service.get_attendance_records(
            db=db,
            start_date=start_date,
            end_date=end_date,
            limit=1000  # 限制批量处理数量
        )
        
        total_exceptions = 0
        processed_records = 0
        
        for record in records:
            try:
                exceptions = exception_detection_service.detect_attendance_exceptions(
                    db=db,
                    record_id=record.record_id
                )
                
                exception_detection_service.update_record_status_based_on_exceptions(
                    db=db,
                    record_id=record.record_id,
                    exceptions=exceptions
                )
                
                total_exceptions += len(exceptions)
                processed_records += 1
                
            except Exception as e:
                print(f"处理记录 {record.record_id} 时出错: {str(e)}")
                continue
        
        return {
            "status": "success",
            "message": f"批量异常检测完成",
            "processed_records": processed_records,
            "total_exceptions": total_exceptions,
            "details": {
                "start_date": start_date,
                "end_date": end_date,
                "total_records_found": len(records)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量异常检测失败: {str(e)}")