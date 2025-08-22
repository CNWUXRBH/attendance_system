from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from fastapi.responses import StreamingResponse

from database.database import get_db
from schemas import attendance_record as attendance_record_schema
from services import attendance_service

router = APIRouter()

@router.get("/debug-raw-records")
def debug_raw_attendance_records(db: Session = Depends(get_db)):
    """
    调试用：直接查询考勤记录表，不使用JOIN
    """
    try:
        raw_records = attendance_service.get_attendance_records(db, limit=10)
        return {
            "count": len(raw_records),
            "records": [{
                "record_id": r.record_id,
                "employee_id": r.employee_id,
                "clock_in_time": r.clock_in_time.isoformat() if r.clock_in_time else None,
                "clock_out_time": r.clock_out_time.isoformat() if r.clock_out_time else None,
                "status": r.status
            } for r in raw_records]
        }
    except Exception as e:
        return {
            "error": str(e),
            "count": 0,
            "records": []
        }

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

@router.post("/import")
async def import_attendance_records(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        result = await attendance_service.import_records_from_excel(db, file)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




@router.get("/sync-logs")
def get_sync_logs(limit: int = 50, db: Session = Depends(get_db)):
    """
    获取同步日志
    """
    try:
        from services.mssql_sync_service import mssql_sync_service
        logs = mssql_sync_service.get_sync_logs(db, limit=limit)
        
        return {
            "success": True,
            "logs": [
                {
                    "id": log.id,
                    "sync_date": log.sync_date.isoformat() if log.sync_date else None,
                    "employee_count": log.employee_count,
                    "record_count": log.record_count,
                    "success_count": log.success_count,
                    "error_count": log.error_count,
                    "status": log.status,
                    "error_message": log.error_message,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in logs
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取同步日志失败: {str(e)}",
            "logs": []
        }

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


@router.get("/test-attendance-status")
def test_attendance_status(
    clock_in_time: str,
    clock_out_time: str,
    db: Session = Depends(get_db)
):
    """
    测试考勤状态判断逻辑
    示例: /test-attendance-status?clock_in_time=2025-08-20T08:33:25&clock_out_time=2025-08-20T17:38:03
    """
    try:
        from services.mssql_sync_service import mssql_sync_service
        from datetime import datetime
        
        # 解析时间字符串
        clock_in = datetime.fromisoformat(clock_in_time.replace('Z', '+00:00'))
        clock_out = datetime.fromisoformat(clock_out_time.replace('Z', '+00:00'))
        
        # 计算工作时长
        work_duration = (clock_out - clock_in).total_seconds() / 3600
        
        # 获取考勤状态
        status = mssql_sync_service._calculate_attendance_status(clock_in, clock_out)
        
        # 识别班制类型
        shift_type = mssql_sync_service._identify_shift_type(clock_in, clock_out)
        
        return {
            "clock_in_time": clock_in.isoformat(),
            "clock_out_time": clock_out.isoformat(),
            "work_duration_hours": round(work_duration, 2),
            "shift_type": shift_type,
            "attendance_status": status,
            "analysis": {
                "is_late": clock_in.hour > 9 or (clock_in.hour == 9 and clock_in.minute > 0),
                "is_early": (clock_out.hour < 17) or (clock_out.hour == 17 and clock_out.minute < 15),
                "meets_work_hours": work_duration >= 8
            }
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/", response_model=List[attendance_record_schema.AttendanceRecordResponse])
def read_attendance_records(
    skip: int = 0,
    limit: int = 100,
    employee_id: int = None,
    name: str = None,
    startDate: str = None,
    endDate: str = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    # 处理前端传递的参数格式
    if startDate and not start_date:
        try:
            start_date = date.fromisoformat(startDate)
        except ValueError:
            pass
    if endDate and not end_date:
        try:
            end_date = date.fromisoformat(endDate)
        except ValueError:
            pass
    
    records = attendance_service.get_attendance_records_formatted(
        db, skip=skip, limit=limit, employee_id=employee_id, 
        name=name, start_date=start_date, end_date=end_date
    )
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