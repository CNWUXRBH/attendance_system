from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database.database import Base

class SyncLog(Base):
    """
    同步日志模型
    用于记录考勤数据同步操作的日志，防止重复同步
    """
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sync_type = Column(String(50), nullable=False, comment="同步类型，如：attendance_records")
    sync_source = Column(String(100), nullable=False, comment="同步数据源，如：MSSQL_AttendanceDB")
    sync_date = Column(String(10), nullable=False, comment="同步的数据日期，格式：YYYY-MM-DD")
    employee_no = Column(String(50), nullable=True, comment="员工工号，如果是按员工同步")
    sync_status = Column(String(20), nullable=False, default="processing", comment="同步状态：processing, success, failed")
    records_count = Column(Integer, default=0, comment="同步的记录数量")
    error_message = Column(Text, nullable=True, comment="错误信息")
    sync_start_time = Column(DateTime, nullable=False, default=func.now(), comment="同步开始时间")
    sync_end_time = Column(DateTime, nullable=True, comment="同步结束时间")
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SyncLog(id={self.id}, sync_type='{self.sync_type}', sync_date='{self.sync_date}', status='{self.sync_status}')>"

class SyncRecord(Base):
    """
    同步记录详情模型
    记录每条具体的同步数据，用于去重和追踪
    """
    __tablename__ = "sync_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sync_log_id = Column(Integer, nullable=False, comment="关联的同步日志ID")
    employee_no = Column(String(50), nullable=False, comment="员工工号")
    attendance_date = Column(String(10), nullable=False, comment="考勤日期，格式：YYYY-MM-DD")
    clock_in_time = Column(DateTime, nullable=True, comment="上班打卡时间")
    clock_out_time = Column(DateTime, nullable=True, comment="下班打卡时间")
    external_record_id = Column(String(100), nullable=True, comment="外部系统的记录ID")
    sync_hash = Column(String(64), nullable=False, unique=True, comment="同步数据的哈希值，用于去重")
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<SyncRecord(id={self.id}, employee_no='{self.employee_no}', attendance_date='{self.attendance_date}')>"