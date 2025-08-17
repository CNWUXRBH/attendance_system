from sqlalchemy.orm import Session
from typing import List, Optional

from models import notification as notification_model, employee as employee_model
from schemas import notification as notification_schema
from services.email_service import send_email

def create_notification(db: Session, notification: notification_schema.NotificationCreate):
    # 只发送邮件通知，不存储站内通知
    employee = db.query(employee_model.Employee).filter(employee_model.Employee.employee_id == notification.employee_id).first()
    if employee and employee.email:
        send_email(employee.email, "考勤异常预警", notification.message)
        return {"status": "email_sent", "employee_id": notification.employee_id, "message": notification.message}
    else:
        return {"status": "email_failed", "employee_id": notification.employee_id, "message": "员工邮箱信息不存在"}

def get_notifications_by_employee(db: Session, employee_id: int, skip: int = 0, limit: int = 100):
    return db.query(notification_model.Notification).filter(notification_model.Notification.employee_id == employee_id).offset(skip).limit(limit).all()

def mark_notification_as_read(db: Session, notification_id: int):
    db_notification = db.query(notification_model.Notification).filter(notification_model.Notification.notification_id == notification_id).first()
    if db_notification:
        db_notification.is_read = True
        db.commit()
        db.refresh(db_notification)
    return db_notification