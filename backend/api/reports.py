from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database.database import get_db
from services import report_service
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/")
def get_reports(db: Session = Depends(get_db)):
    return report_service.get_reports(db)

@router.post("/")
def generate_report(report_data: dict, db: Session = Depends(get_db)):
    report_type = report_data.get("report_type")
    start_date = report_data.get("start_date")
    end_date = report_data.get("end_date")
    
    if not report_type:
        raise HTTPException(status_code=400, detail="report_type is required")
    
    return report_service.generate_report(db, report_type, start_date, end_date)

@router.get("/detailed")
def get_detailed_report(start_date: str, end_date: str, db: Session = Depends(get_db)):
    try:
        s_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        e_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    report_data = report_service.get_detailed_report_data(db, s_date, e_date)
    return report_data

@router.get("/export_detailed")
def export_detailed_report(start_date: str, end_date: str, db: Session = Depends(get_db)):
    try:
        s_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        e_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    report_data = report_service.get_detailed_report_data(db, s_date, e_date)
    output = report_service.export_detailed_report_to_excel(report_data)

    if output is None:
        raise HTTPException(status_code=404, detail="No data to export.")

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=detailed_report_{start_date}_to_{end_date}.xlsx"})

@router.get("/download/{report_id}")
def download_report(report_id: str, db: Session = Depends(get_db)):
    """下载报表文件"""
    # 这里可以根据report_id获取具体的报表数据并生成Excel文件
    # 为了演示，我们生成一个简单的Excel文件
    import pandas as pd
    from io import BytesIO
    
    # 创建示例数据
    data = {
        '报表ID': [report_id],
        '生成时间': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        '状态': ['已生成']
    }
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='报表数据')
    output.seek(0)
    
    return StreamingResponse(
        BytesIO(output.read()), 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.xlsx"}
    )

@router.get("/view/{report_id}")
def view_report(report_id: str, db: Session = Depends(get_db)):
    """查看报表详情"""
    # 返回报表的详细信息
    return {
        "success": True,
        "report_id": report_id,
        "generated_at": datetime.now().isoformat(),
        "status": "completed",
        "data": {
            "summary": f"报表 {report_id} 的详细信息",
            "records_count": 100,
            "date_range": "2025-01-01 至 2025-01-31"
        }
    }