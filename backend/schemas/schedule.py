from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

# 导入模型中的枚举
class ScheduleStatusEnum(str, Enum):
    """排班状态枚举"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class SchedulePriorityEnum(str, Enum):
    """排班优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class ScheduleBase(BaseModel):
    employee_id: int
    shift_type_id: int
    start_date: datetime
    end_date: datetime
    status: Optional[ScheduleStatusEnum] = ScheduleStatusEnum.DRAFT
    priority: Optional[SchedulePriorityEnum] = SchedulePriorityEnum.NORMAL
    notes: Optional[str] = None
    tags: Optional[str] = None
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('结束时间必须晚于开始时间')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 500:
            raise ValueError('标签长度不能超过500个字符')
        return v

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    employee_id: Optional[int] = None
    shift_type_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ScheduleStatusEnum] = None
    priority: Optional[SchedulePriorityEnum] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date'] and v <= values['start_date']:
            raise ValueError('结束时间必须晚于开始时间')
        return v

class ScheduleStatusTransition(BaseModel):
    """状态转换请求"""
    new_status: ScheduleStatusEnum
    approved_by: Optional[int] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None

class ScheduleBatchOperation(BaseModel):
    """批量操作请求"""
    schedule_ids: List[int]
    operation: str  # 'approve', 'reject', 'cancel', 'publish'
    approved_by: Optional[int] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None

class Schedule(ScheduleBase):
    schedule_id: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # 关联对象（可选，用于返回详细信息）
    employee_name: Optional[str] = None
    shift_type_name: Optional[str] = None
    approver_name: Optional[str] = None
    
    # 状态显示
    status_display: Optional[str] = None
    priority_display: Optional[str] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True

class ScheduleStatistics(BaseModel):
    """排班统计信息"""
    total_schedules: int
    status_counts: dict
    priority_counts: dict
    employee_schedule_counts: dict
    daily_schedule_counts: dict
    
class ScheduleConflictInfo(BaseModel):
    """排班冲突信息"""
    has_conflict: bool
    overlap_conflict: Optional[dict] = None
    rest_time_conflict: Optional[dict] = None
    daily_hours_exceeded: bool = False
    weekly_hours_exceeded: bool = False
    details: List[str] = []

class BatchOperationResult(BaseModel):
    """批量操作结果"""
    success_count: int
    conflict_count: int
    error_count: int
    created_schedules: List[dict] = []
    conflicts: List[dict] = []
    errors: List[dict] = []