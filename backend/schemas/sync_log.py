from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SyncLogBase(BaseModel):
    sync_type: str
    sync_source: str
    sync_date: str
    employee_no: Optional[str] = None
    sync_status: str = "processing"
    records_count: int = 0
    error_message: Optional[str] = None

class SyncLogCreate(SyncLogBase):
    pass

class SyncLogUpdate(BaseModel):
    sync_status: Optional[str] = None
    records_count: Optional[int] = None
    error_message: Optional[str] = None
    sync_end_time: Optional[datetime] = None

class SyncLog(SyncLogBase):
    id: int
    sync_start_time: datetime
    sync_end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SyncRecordBase(BaseModel):
    sync_log_id: int
    employee_no: str
    attendance_date: str
    clock_in_time: Optional[datetime] = None
    clock_out_time: Optional[datetime] = None
    external_record_id: Optional[str] = None
    sync_hash: str

class SyncRecordCreate(SyncRecordBase):
    pass

class SyncRecord(SyncRecordBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SyncResponse(BaseModel):
    message: str
    sync_log_id: int
    records_count: int
    status: str
    duplicates_skipped: int = 0