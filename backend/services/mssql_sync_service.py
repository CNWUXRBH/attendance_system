from datetime import datetime, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import hashlib
import logging

from database.mssql_database import get_mssql_connection
from models import employee as employee_model
from models import attendance_record as attendance_record_model
from models.sync_log import SyncLog, SyncRecord
from schemas.sync_log import SyncLogCreate, SyncLogUpdate, SyncRecordCreate

logger = logging.getLogger(__name__)

class MSSQLSyncService:
    """
    MSSQL数据同步服务
    """
    
    def __init__(self):
        self.mssql_conn = get_mssql_connection()
    
    def sync_attendance_records(self, db: Session, sync_date: str = None, employee_nos: List[str] = None) -> Dict:
        """
        从MSSQL同步考勤记录
        
        Args:
            db: SQLAlchemy数据库会话
            sync_date: 同步日期，格式：YYYY-MM-DD，默认为今天
            employee_nos: 指定员工工号列表，为空则同步所有员工
        
        Returns:
            同步结果字典
        """
        if sync_date is None:
            sync_date = date.today().strftime('%Y-%m-%d')
        
        # 创建同步日志
        sync_log = self._create_sync_log(db, sync_date, employee_nos)
        
        try:
            # 获取系统中的员工列表
            if employee_nos:
                employees = db.query(employee_model.Employee).filter(
                    employee_model.Employee.employee_no.in_(employee_nos)
                ).all()
            else:
                employees = db.query(employee_model.Employee).all()
            
            if not employees:
                self._update_sync_log(db, sync_log.id, {
                    "sync_status": "failed",
                    "error_message": "未找到要同步的员工",
                    "sync_end_time": datetime.now()
                })
                return {
                    "message": "未找到要同步的员工",
                    "sync_log_id": sync_log.id,
                    "records_count": 0,
                    "status": "failed"
                }
            
            # 从MSSQL获取考勤数据
            attendance_data = self._fetch_attendance_from_mssql(sync_date, [emp.employee_no for emp in employees])
            
            # 检查是否获取到数据，如果没有数据可能是连接失败
            if not attendance_data:
                # 测试MSSQL连接状态
                if not self.test_mssql_connection():
                    self._update_sync_log(db, sync_log.id, {
                        "sync_status": "failed",
                        "error_message": "MSSQL数据库连接失败，无法获取考勤数据",
                        "sync_end_time": datetime.now()
                    })
                    return {
                        "message": "MSSQL数据库连接失败，同步失败",
                        "sync_log_id": sync_log.id,
                        "records_count": 0,
                        "status": "failed"
                    }
                else:
                    # 连接正常但没有数据
                    self._update_sync_log(db, sync_log.id, {
                        "sync_status": "success",
                        "records_count": 0,
                        "sync_end_time": datetime.now()
                    })
                    return {
                        "message": "同步完成，但没有找到符合条件的考勤数据",
                        "sync_log_id": sync_log.id,
                        "records_count": 0,
                        "status": "success"
                    }
            
            # 处理同步数据
            result = self._process_sync_data(db, sync_log.id, attendance_data, employees)
            
            # 更新同步日志
            self._update_sync_log(db, sync_log.id, {
                "sync_status": "success",
                "records_count": result["records_count"],
                "sync_end_time": datetime.now()
            })
            
            result["sync_log_id"] = sync_log.id
            return result
            
        except Exception as e:
            logger.error(f"同步失败: {str(e)}")
            self._update_sync_log(db, sync_log.id, {
                "sync_status": "failed",
                "error_message": str(e),
                "sync_end_time": datetime.now()
            })
            raise
    
    def _create_sync_log(self, db: Session, sync_date: str, employee_nos: List[str] = None) -> SyncLog:
        """
        创建同步日志记录
        """
        sync_log_data = SyncLogCreate(
            sync_type="attendance_records",
            sync_source="MSSQL_AttendanceDB",
            sync_date=sync_date,
            employee_no=",".join(employee_nos) if employee_nos else "all"
        )
        
        sync_log = SyncLog(**sync_log_data.dict())
        db.add(sync_log)
        db.commit()
        db.refresh(sync_log)
        
        return sync_log
    
    def _update_sync_log(self, db: Session, sync_log_id: int, update_data: Dict):
        """
        更新同步日志
        """
        db.query(SyncLog).filter(SyncLog.id == sync_log_id).update(update_data)
        db.commit()
    
    def _fetch_attendance_from_mssql(self, sync_date: str, employee_nos: List[str]) -> List[Dict]:
        """
        从MSSQL数据库获取考勤数据
        
        根据实际的MSSQL表结构，只有CardTime字段记录刷卡时间
        需要处理每个员工当天的第一次刷卡为上班时间，最后一次刷卡为下班时间
        """
        try:
            # 构建员工工号的IN条件
            employee_nos_str = "','".join(employee_nos)
            
            # 查询所有刷卡记录，按员工和时间排序
            query = f"""
            SELECT 
                EmployeeID as employee_no,
                EmployeeName as employee_name,
                DeviceID as device_id,
                DeviceName as device_name,
                CardTime as card_time
            FROM [考勤记录表] 
            WHERE CAST(CardTime AS DATE) = ? 
            AND EmployeeID IN ('{employee_nos_str}')
            ORDER BY EmployeeID, CardTime
            """
            
            # 执行查询获取所有刷卡记录
            raw_records = self.mssql_conn.execute_query(query, (sync_date,))
            
            # 处理刷卡记录，计算上下班时间
            processed_records = self._process_card_records(raw_records, sync_date)
            
            logger.info(f"从MSSQL获取到 {len(raw_records)} 条刷卡记录，处理后得到 {len(processed_records)} 条考勤记录")
            return processed_records
            
        except Exception as e:
            logger.error(f"从MSSQL获取数据失败: {str(e)}")
            # 如果MSSQL连接失败，返回空列表
            logger.warning("MSSQL连接失败，无法获取考勤数据")
            return []
    
    def _process_card_records(self, raw_records: List[Dict], sync_date: str) -> List[Dict]:
        """
        处理刷卡记录，将每个员工当天的第一次刷卡作为上班时间，最后一次刷卡作为下班时间
        """
        from collections import defaultdict
        
        # 按员工分组刷卡记录
        employee_records = defaultdict(list)
        for record in raw_records:
            employee_no = record['employee_no']
            employee_records[employee_no].append(record)
        
        processed_records = []
        
        for employee_no, records in employee_records.items():
            if not records:
                continue
                
            # 按时间排序（确保第一条是最早的，最后一条是最晚的）
            records.sort(key=lambda x: x['card_time'])
            
            # 第一次刷卡作为上班时间
            clock_in_time = records[0]['card_time']
            
            # 最后一次刷卡作为下班时间（如果只有一次刷卡，则下班时间为空）
            clock_out_time = records[-1]['card_time'] if len(records) > 1 else None
            
            # 生成唯一的外部记录ID
            external_record_id = f"MSSQL_{employee_no}_{sync_date}_{len(records)}_cards"
            
            processed_record = {
                'employee_no': employee_no,
                'employee_name': records[0].get('employee_name', ''),
                'attendance_date': sync_date,
                'clock_in_time': clock_in_time,
                'clock_out_time': clock_out_time,
                'external_record_id': external_record_id,
                'total_card_count': len(records),
                'device_info': f"{records[0].get('device_name', '')}等{len(set(r.get('device_name', '') for r in records))}个设备"
            }
            
            processed_records.append(processed_record)
            
        return processed_records
    

    
    def _process_sync_data(self, db: Session, sync_log_id: int, attendance_data: List[Dict], employees: List) -> Dict:
        """
        处理同步数据，去重并插入数据库
        """
        records_count = 0
        duplicates_skipped = 0
        
        # 创建员工工号到ID的映射
        employee_map = {emp.employee_no: emp.employee_id for emp in employees}
        
        for record in attendance_data:
            employee_no = record['employee_no']
            
            if employee_no not in employee_map:
                logger.warning(f"员工工号 {employee_no} 在系统中不存在，跳过")
                continue
            
            # 生成数据哈希用于去重
            sync_hash = self._generate_sync_hash(record)
            
            # 检查是否已经同步过
            existing_record = db.query(SyncRecord).filter(
                SyncRecord.sync_hash == sync_hash
            ).first()
            
            if existing_record:
                duplicates_skipped += 1
                logger.debug(f"记录已存在，跳过: {employee_no} - {record['attendance_date']}")
                continue
            
            # 创建考勤记录
            attendance_record = attendance_record_model.AttendanceRecord(
                employee_id=employee_map[employee_no],
                clock_in_time=record.get('clock_in_time'),
                clock_out_time=record.get('clock_out_time'),
                clock_type="正常",
                device_id="MSSQL_SYNC",
                location="MSSQL同步",
                status=self._determine_status(record)
            )
            
            db.add(attendance_record)
            
            # 创建同步记录
            sync_record = SyncRecord(
                sync_log_id=sync_log_id,
                employee_no=employee_no,
                attendance_date=record['attendance_date'],
                clock_in_time=record.get('clock_in_time'),
                clock_out_time=record.get('clock_out_time'),
                external_record_id=record.get('external_record_id'),
                sync_hash=sync_hash
            )
            
            db.add(sync_record)
            records_count += 1
        
        db.commit()
        
        return {
            "message": f"成功同步 {records_count} 条记录，跳过重复记录 {duplicates_skipped} 条",
            "records_count": records_count,
            "duplicates_skipped": duplicates_skipped,
            "status": "success"
        }
    
    def _generate_sync_hash(self, record: Dict) -> str:
        """
        生成同步数据的哈希值用于去重
        """
        hash_string = f"{record['employee_no']}_{record['attendance_date']}_{record.get('clock_in_time')}_{record.get('clock_out_time')}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _determine_status(self, record: Dict) -> str:
        """
        根据考勤时间判断状态
        """
        clock_in_time = record.get('clock_in_time')
        clock_out_time = record.get('clock_out_time')
        
        if not clock_in_time and not clock_out_time:
            return "缺勤"
        elif not clock_in_time:
            return "缺卡"
        elif not clock_out_time:
            return "缺卡"
        
        # 简单的迟到早退判断（可以根据实际规则调整）
        if isinstance(clock_in_time, datetime):
            if clock_in_time.hour > 9 or (clock_in_time.hour == 9 and clock_in_time.minute > 0):
                if isinstance(clock_out_time, datetime) and clock_out_time.hour < 18:
                    return "迟到早退"
                return "迟到"
        
        if isinstance(clock_out_time, datetime) and clock_out_time.hour < 18:
            return "早退"
        
        return "正常"
    
    def get_sync_logs(self, db: Session, limit: int = 50) -> List[SyncLog]:
        """
        获取同步日志列表
        """
        return db.query(SyncLog).order_by(SyncLog.created_at.desc()).limit(limit).all()
    
    def test_mssql_connection(self) -> bool:
        """
        测试MSSQL连接
        """
        return self.mssql_conn.test_connection()

# 全局同步服务实例
mssql_sync_service = MSSQLSyncService()