from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.database import get_db
from services import dashboard_service
from typing import Optional

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    date: Optional[str] = Query(None, description="日期筛选，格式：YYYY-MM-DD")
):
    return dashboard_service.get_dashboard_stats(db, date)

@router.get("/exception-stats")
def get_exception_type_stats(
    db: Session = Depends(get_db),
    date: Optional[str] = Query(None, description="日期筛选，格式：YYYY-MM-DD")
):
    return dashboard_service.get_exception_type_stats(db, date)

@router.get("/exception-records")
def get_today_exception_records(
    db: Session = Depends(get_db),
    date: Optional[str] = Query(None, description="日期筛选，格式：YYYY-MM-DD"),
    limit: int = Query(10, description="返回记录数量限制")
):
    return dashboard_service.get_today_exception_records(db, date, limit)