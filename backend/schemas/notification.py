from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    employee_id: int
    message: str

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    notification_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True