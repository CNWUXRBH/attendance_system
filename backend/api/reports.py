from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database.database import get_db
from services import report_service
from fastapi.responses import StreamingResponse
from urllib.parse import quote

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
    import pandas as pd
    from io import BytesIO
    from datetime import datetime, timedelta
    
    # 根据report_id判断报表类型（简化处理）
    # 实际应用中应该从数据库获取报表信息
    if 'monthly' in report_id or report_id.startswith('1'):
        # 月度考勤报表
        report_type = 'monthly'
        filename = f'月度考勤报表_{report_id}.xlsx'
        sheet_name = '月度考勤报表'
        
        # 获取真实的月度考勤数据
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        report_data = report_service.get_detailed_report_data(db, start_date, end_date)
        
    else:
        # 异常考勤统计
        report_type = 'exception'
        filename = f'异常考勤统计_{report_id}.xlsx'
        sheet_name = '异常考勤统计'
        
        # 获取真实的异常考勤数据
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        all_data = report_service.get_detailed_report_data(db, start_date, end_date)
        # 过滤只保留异常记录
        report_data = [r for r in all_data if r['status'] in ['迟到', '早退', '缺勤']]
    
    if not report_data:
        # 如果没有数据，创建空的示例数据
        report_data = [{
            'employee_name': '暂无数据',
            'clock_in_time': datetime.now(),
            'clock_out_time': datetime.now(),
            'work_duration': '0:00:00',
            'overtime': '0:00:00',
            'status': '正常',
            'shift_name': '标准班次'
        }]
    
    # 转换为DataFrame
    df_data = []
    for record in report_data:
        df_data.append({
            '员工姓名': record['employee_name'],
            '上班时间': record['clock_in_time'].strftime('%Y-%m-%d %H:%M:%S') if record['clock_in_time'] else '',
            '下班时间': record['clock_out_time'].strftime('%Y-%m-%d %H:%M:%S') if record['clock_out_time'] else '',
            '工作时长': str(record['work_duration']),
            '加班时长': str(record['overtime']),
            '考勤状态': record['status'],
            '班次名称': record['shift_name']
        })
    
    df = pd.DataFrame(df_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    
    # 对中文文件名进行URL编码
    encoded_filename = quote(filename.encode('utf-8'))
    
    return StreamingResponse(
        BytesIO(output.read()), 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )

@router.get("/view/{report_id}")
def view_report(report_id: str, db: Session = Depends(get_db)):
    """查看报表详情"""
    from datetime import datetime, timedelta
    
    # 根据report_id判断报表类型
    if 'monthly' in report_id or report_id.startswith('1'):
        # 月度考勤报表
        report_type = 'monthly'
        report_name = '月度考勤报表'
        
        # 获取真实的月度考勤数据统计
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        report_data = report_service.get_detailed_report_data(db, start_date, end_date)
        
        records_count = len(report_data)
        summary = f"月度考勤报表包含 {records_count} 条考勤记录，涵盖所有员工的考勤情况"
        
    else:
        # 异常考勤统计
        report_type = 'exception'
        report_name = '异常考勤统计'
        
        # 获取真实的异常考勤数据统计
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        all_data = report_service.get_detailed_report_data(db, start_date, end_date)
        report_data = [r for r in all_data if r['status'] in ['迟到', '早退', '缺勤']]
        
        records_count = len(report_data)
        total_records = len(all_data)
        summary = f"异常考勤统计发现 {records_count} 条异常记录，占总记录数 {total_records} 的 {(records_count/total_records*100):.1f}%" if total_records > 0 else "异常考勤统计暂无异常记录"
    
    return {
        "success": True,
        "report_id": report_id,
        "generated_at": datetime.now().isoformat(),
        "status": "completed",
        "data": {
            "summary": summary,
            "records_count": records_count,
            "date_range": f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
            "report_type": report_type,
            "report_name": report_name
        }
    }