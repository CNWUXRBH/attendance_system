from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas import notification as notification_schema
from services import notification_service

router = APIRouter()

@router.post("/", response_model=notification_schema.Notification)
def create_notification(notification: notification_schema.NotificationCreate, db: Session = Depends(get_db)):
    return notification_service.create_notification(db=db, notification=notification)

@router.get("/{employee_id}", response_model=List[notification_schema.Notification])
def read_notifications(employee_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notifications = notification_service.get_notifications_by_employee(db, employee_id=employee_id, skip=skip, limit=limit)
    return notifications

@router.put("/{notification_id}/read", response_model=notification_schema.Notification)
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    db_notification = notification_service.mark_notification_as_read(db, notification_id=notification_id)
    if db_notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_notification