from sqlalchemy import Column, Integer, String, Date, ForeignKey, DATETIME, func, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.database import Base
import enum

class ScheduleStatus(enum.Enum):
    """排班状态枚举"""
    ACTIVE = "active"            # 生效中
    COMPLETED = "completed"      # 已完成
    CANCELLED = "cancelled"      # 已取消

class SchedulePriority(enum.Enum):
    """排班优先级枚举"""
    LOW = "low"        # 低优先级
    NORMAL = "normal"  # 普通优先级
    HIGH = "high"      # 高优先级
    URGENT = "urgent"  # 紧急

class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    shift_type_id = Column(Integer, ForeignKey("shift_types.shift_type_id"), nullable=False)
    start_date = Column(DATETIME, nullable=False)  # 改为DATETIME支持具体时间
    end_date = Column(DATETIME, nullable=False)    # 改为DATETIME支持具体时间
    
    # 状态管理字段
    status = Column(SQLEnum(ScheduleStatus), default=ScheduleStatus.ACTIVE, nullable=False)
    priority = Column(SQLEnum(SchedulePriority), default=SchedulePriority.NORMAL, nullable=False)
    
    # 其他字段
    notes = Column(Text, nullable=True)  # 备注
    tags = Column(String(500), nullable=True)  # 标签，用逗号分隔
    
    # 时间戳
    created_at = Column(DATETIME, server_default=func.now())
    updated_at = Column(DATETIME, server_default=func.now(), onupdate=func.now())
    
    # 关系
    employee = relationship("Employee", foreign_keys=[employee_id])
    shift_type = relationship("ShiftType")
    
    def can_transition_to(self, new_status: ScheduleStatus) -> bool:
        """检查是否可以转换到新状态"""
        valid_transitions = {
            ScheduleStatus.ACTIVE: [ScheduleStatus.COMPLETED, ScheduleStatus.CANCELLED],
            ScheduleStatus.COMPLETED: [],  # 完成状态不能转换
            ScheduleStatus.CANCELLED: [ScheduleStatus.ACTIVE]  # 取消后可以重新激活
        }
        
        return new_status in valid_transitions.get(self.status, [])
    
    def get_status_display(self) -> str:
        """获取状态的中文显示"""
        status_display = {
            ScheduleStatus.ACTIVE: "生效中",
            ScheduleStatus.COMPLETED: "已完成",
            ScheduleStatus.CANCELLED: "已取消"
        }
        return status_display.get(self.status, "未知状态")
    
    def get_priority_display(self) -> str:
        """获取优先级的中文显示"""
        priority_display = {
            SchedulePriority.LOW: "低优先级",
            SchedulePriority.NORMAL: "普通",
            SchedulePriority.HIGH: "高优先级",
            SchedulePriority.URGENT: "紧急"
        }
        return priority_display.get(self.priority, "未知优先级")