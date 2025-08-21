from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import hashlib
import logging
import threading
import time
import asyncio
from enum import Enum
import traceback
import os

from database.mssql_database import get_mssql_connection
from models import employee as employee_model
from models import attendance_record as attendance_record_model
from models.sync_log import SyncLog, SyncRecord
from schemas.sync_log import SyncLogCreate, SyncLogUpdate, SyncRecordCreate

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SyncErrorType(Enum):
    """同步错误类型枚举"""
    CONNECTION_ERROR = "connection_error"  # 连接错误
    DATA_ERROR = "data_error"  # 数据错误
    TIMEOUT_ERROR = "timeout_error"  # 超时错误
    PERMISSION_ERROR = "permission_error"  # 权限错误
    UNKNOWN_ERROR = "unknown_error"  # 未知错误

class SyncMetrics:
    """同步监控指标"""
    def __init__(self):
        self.total_syncs = 0
        self.successful_syncs = 0
        self.failed_syncs = 0
        self.total_records_processed = 0
        self.total_errors = 0
        self.error_types = {}
        self.last_error_time = None
        self.consecutive_failures = 0
        
    def record_sync_start(self):
        self.total_syncs += 1
        
    def record_sync_success(self, records_count: int = 0):
        self.successful_syncs += 1
        self.total_records_processed += records_count
        self.consecutive_failures = 0
        
    def record_sync_failure(self, error_type: SyncErrorType, error_msg: str = None):
        self.failed_syncs += 1
        self.total_errors += 1
        self.consecutive_failures += 1
        self.last_error_time = datetime.now()
        
        error_key = error_type.value
        if error_key not in self.error_types:
            self.error_types[error_key] = 0
        self.error_types[error_key] += 1
        
    def get_metrics(self) -> Dict:
        success_rate = (self.successful_syncs / self.total_syncs * 100) if self.total_syncs > 0 else 0
        return {
            "total_syncs": self.total_syncs,
            "successful_syncs": self.successful_syncs,
            "failed_syncs": self.failed_syncs,
            "success_rate": round(success_rate, 2),
            "total_records_processed": self.total_records_processed,
            "total_errors": self.total_errors,
            "error_types": self.error_types,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "consecutive_failures": self.consecutive_failures
        }

class MSSQLSyncService:
    """
    MSSQL数据同步服务
    支持手动同步和后台定时同步
    """
    
    def __init__(self):
        self.mssql_conn = get_mssql_connection()
        # 后台同步相关属性
        self._background_sync_thread = None
        
        # 根据环境设置同步间隔
        self._sync_interval = self._get_sync_interval_by_env()
        self._is_running = False
        self._stop_event = threading.Event()
        self._last_sync_time = None
        self._sync_status = "stopped"
        
        # 监控和错误处理相关属性
        self._metrics = SyncMetrics()
        self._max_retries = 3
        self._retry_delay = 30  # 重试延迟（秒）
        self._health_check_enabled = True
        
        # 记录当前环境和同步间隔
        env_name = self._get_environment_name()
        logger.info(f"同步服务初始化 - 环境: {env_name}, 同步间隔: {self._sync_interval//60}分钟({self._sync_interval}秒)")
    
    def sync_attendance_records(self, db: Session, sync_date: str = None, employee_nos: List[str] = None, sync_days: int = 1) -> Dict:
        """
        从MSSQL同步考勤记录
        
        Args:
            db: SQLAlchemy数据库会话
            sync_date: 同步日期，格式：YYYY-MM-DD，默认为今天
            employee_nos: 指定员工工号列表，为空则同步所有员工
            sync_days: 同步天数，默认1天（当天）
        
        Returns:
            同步结果字典
        """
        if sync_date is None:
            # 默认同步指定天数的数据，从今天往前推
            end_date = date.today()
            start_date = end_date - timedelta(days=sync_days - 1)
            return self._sync_date_range(db, start_date, end_date, employee_nos)
        else:
            # 如果指定了日期，只同步该日期
            return self._sync_single_date(db, sync_date, employee_nos)
    
    def _sync_date_range(self, db: Session, start_date: date, end_date: date, employee_nos: List[str] = None) -> Dict:
        """
        同步日期范围内的考勤记录
        """
        total_records = 0
        total_duplicates = 0
        failed_dates = []
        successful_dates = []
        
        # 创建总体同步日志
        date_range_str = f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
        sync_log = self._create_sync_log(db, date_range_str, employee_nos)
        
        try:
            current_date = start_date
            while current_date <= end_date:
                sync_date_str = current_date.strftime('%Y-%m-%d')
                logger.info(f"开始同步日期: {sync_date_str}")
                
                try:
                    result = self._sync_single_date_internal(db, sync_date_str, employee_nos)
                    total_records += result.get('records_count', 0)
                    total_duplicates += result.get('duplicates_skipped', 0)
                    successful_dates.append(sync_date_str)
                except Exception as e:
                    logger.error(f"同步日期 {sync_date_str} 失败: {str(e)}")
                    failed_dates.append(sync_date_str)
                
                current_date += timedelta(days=1)
            
            # 更新总体同步日志
            status = "success" if not failed_dates else "partial_success" if successful_dates else "failed"
            message = f"成功同步 {len(successful_dates)} 天，失败 {len(failed_dates)} 天。总计 {total_records} 条记录，跳过重复 {total_duplicates} 条"
            
            self._update_sync_log(db, sync_log.id, {
                "sync_status": status,
                "records_count": total_records,
                "error_message": f"失败日期: {', '.join(failed_dates)}" if failed_dates else None,
                "sync_end_time": datetime.now()
            })
            
            return {
                "message": message,
                "sync_log_id": sync_log.id,
                "records_count": total_records,
                "duplicates_skipped": total_duplicates,
                "successful_dates": successful_dates,
                "failed_dates": failed_dates,
                "status": status
            }
            
        except Exception as e:
            logger.error(f"批量同步失败: {str(e)}")
            self._update_sync_log(db, sync_log.id, {
                "sync_status": "failed",
                "error_message": str(e),
                "sync_end_time": datetime.now()
            })
            raise
    
    def _sync_single_date(self, db: Session, sync_date: str, employee_nos: List[str] = None) -> Dict:
        """
        同步单个日期的考勤记录（对外接口）
        """
        sync_log = self._create_sync_log(db, sync_date, employee_nos)
        
        try:
            result = self._sync_single_date_internal(db, sync_date, employee_nos)
            
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
    
    def _sync_single_date_internal(self, db: Session, sync_date: str, employee_nos: List[str] = None) -> Dict:
        """
        同步单个日期的考勤记录（内部实现）
        """
        # 获取系统中的员工列表
        if employee_nos:
            employees = db.query(employee_model.Employee).filter(
                employee_model.Employee.employee_no.in_(employee_nos)
            ).all()
        else:
            employees = db.query(employee_model.Employee).all()
        
        if not employees:
            return {
                "message": "未找到要同步的员工",
                "records_count": 0,
                "duplicates_skipped": 0,
                "status": "failed"
            }
        
        # 从MSSQL获取考勤数据
        attendance_data = self._fetch_attendance_from_mssql(sync_date, [emp.employee_no for emp in employees])
        
        # 检查是否获取到数据，如果没有数据可能是连接失败
        if not attendance_data:
            # 测试MSSQL连接状态
            if not self.test_mssql_connection():
                return {
                    "message": "MSSQL数据库连接失败，同步失败",
                    "records_count": 0,
                    "duplicates_skipped": 0,
                    "status": "failed"
                }
            else:
                # 连接正常但没有数据
                return {
                    "message": "同步完成，但没有找到符合条件的考勤数据",
                    "records_count": 0,
                    "duplicates_skipped": 0,
                    "status": "success"
                }
        
        # 处理同步数据（这里需要临时创建一个sync_log_id，在批量同步时不会用到）
        result = self._process_sync_data(db, 0, attendance_data, employees)
        
        return {
            "message": f"同步完成，共处理 {result['records_count']} 条记录，跳过重复 {result.get('duplicates_skipped', 0)} 条",
            "records_count": result["records_count"],
            "duplicates_skipped": result.get("duplicates_skipped", 0),
            "status": "success"
        }
    
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
        
        根据实际的MSSQL表结构，使用TimeRecords、Clocks和Employee表进行关联查询
        需要处理每个员工当天的第一次刷卡为上班时间，最后一次刷卡为下班时间
        """
        try:
            logger.info(f"开始从MSSQL获取考勤数据 - 同步日期: {sync_date}, 员工数量: {len(employee_nos) if employee_nos else 0}")
            
            # 检查员工工号列表是否为空
            if not employee_nos:
                error_msg = "员工工号列表为空，无法查询考勤数据"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # 排除指定的设备ID
            excluded_devices = [701, 702, 703, 704, 705, 706, 710, 750, 760]
            excluded_devices_str = ','.join(map(str, excluded_devices))
            
            # 分批处理员工工号，避免IN子句过长导致查询超时
            batch_size = 100  # 每批处理100个员工
            all_records = []
            
            for i in range(0, len(employee_nos), batch_size):
                batch_employee_nos = employee_nos[i:i + batch_size]
                
                # 构建参数化查询的占位符
                placeholders = ','.join(['?' for _ in batch_employee_nos])
                
                # 根据用户提供的SQL语句结构更新查询，使用参数化查询防止SQL注入
                query = f"""
                SELECT 
                    e.emp_fname as employee_name,
                    T.clock_id as device_id,
                    c.Clock_name as device_name,
                    T.emp_id as employee_no,
                    T.sign_time as card_time
                FROM TimeRecords T WITH (nolock)
                INNER JOIN dbo.Clocks C WITH (nolock) ON C.Clock_id = T.clock_id
                INNER JOIN [dbo].[Employee] e WITH (nolock) ON e.emp_id = t.emp_id
                WHERE CAST(T.sign_time AS DATE) = ?
                AND T.emp_id IN ({placeholders})
                AND T.clock_id NOT IN ({excluded_devices_str})
                ORDER BY T.emp_id, T.sign_time
                """
                
                # 构建查询参数
                params = [sync_date] + batch_employee_nos
                
                try:
                    # 执行查询获取当前批次的刷卡记录
                    batch_records = self.mssql_conn.execute_query(query, params)
                    all_records.extend(batch_records)
                    
                    logger.info(f"批次 {i//batch_size + 1}: 查询员工 {len(batch_employee_nos)} 人，获取到 {len(batch_records)} 条刷卡记录")
                except Exception as batch_error:
                    error_msg = f"批次 {i//batch_size + 1} 查询失败 - 员工数量: {len(batch_employee_nos)}, 错误: {str(batch_error)}"
                    logger.error(error_msg)
                    raise Exception(f"MSSQL批次查询失败: {str(batch_error)}")
            
            # 处理刷卡记录，计算上下班时间
            processed_records = self._process_card_records(all_records, sync_date)
            
            logger.info(f"从MSSQL成功获取到 {len(all_records)} 条刷卡记录，处理后得到 {len(processed_records)} 条考勤记录")
            return processed_records
            
        except Exception as e:
            error_msg = f"从MSSQL获取数据失败 - 同步日期: {sync_date}, 员工数量: {len(employee_nos) if employee_nos else 0}, 错误: {str(e)}"
            logger.error(error_msg)
            # 抛出异常而不是返回空列表，让上层处理
            raise Exception(f"MSSQL数据获取失败: {str(e)}")
    
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
        failed_records = 0
        
        logger.info(f"开始处理同步数据 - 待处理记录数: {len(attendance_data)}, 员工数: {len(employees)}")
        
        # 创建员工工号到ID的映射
        employee_map = {emp.employee_no: emp.employee_id for emp in employees}
        
        for record in attendance_data:
            try:
                employee_no = record['employee_no']
                
                if employee_no not in employee_map:
                    logger.warning(f"员工工号 {employee_no} 在系统中不存在，跳过记录 - 考勤日期: {record.get('attendance_date')}")
                    failed_records += 1
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
                
            except Exception as record_error:
                failed_records += 1
                logger.error(f"处理单条记录失败 - 员工工号: {record.get('employee_no')}, 考勤日期: {record.get('attendance_date')}, 错误: {str(record_error)}")
                continue
        
        try:
            db.commit()
            logger.info(f"数据库提交成功 - 成功: {records_count}条, 重复: {duplicates_skipped}条, 失败: {failed_records}条")
        except Exception as commit_error:
            db.rollback()
            error_msg = f"数据库提交失败: {str(commit_error)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        return {
            "message": f"成功同步 {records_count} 条记录，跳过重复记录 {duplicates_skipped} 条，失败记录 {failed_records} 条",
            "records_count": records_count,
            "duplicates_skipped": duplicates_skipped,
            "failed_records": failed_records,
            "status": "success" if failed_records == 0 else "partial_success"
        }
    
    def _generate_sync_hash(self, record: Dict) -> str:
        """
        生成同步数据的哈希值用于去重
        """
        hash_string = f"{record['employee_no']}_{record['attendance_date']}_{record.get('clock_in_time')}_{record.get('clock_out_time')}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _determine_status(self, record: Dict) -> str:
        """
        根据考勤时间判断状态，支持多班制
        班制规则：
        1. 12H白班：7:00-19:00，迟到线7:30，早退线19:00
        2. 8H班：8:45-17:15，迟到线9:00，早退线17:15
        3. 12H夜班：19:00-7:00，迟到线19:30，早退线7:00
        
        弹性工作规则：
        - 如果员工早到，可以提前下班，但工作时长必须满足对应班制的最低要求
        - 12H班制：最低工作时长12小时
        - 8H班制：最低工作时长8小时
        """
        clock_in_time = record.get('clock_in_time')
        clock_out_time = record.get('clock_out_time')
        
        if not clock_in_time and not clock_out_time:
            return "缺勤"
        elif not clock_in_time:
            return "缺卡"
        elif not clock_out_time:
            return "缺卡"
        
        # 确保时间是datetime对象
        if not isinstance(clock_in_time, datetime) or not isinstance(clock_out_time, datetime):
            return "数据异常"
        
        # 识别班制类型
        shift_type = self._identify_shift_type(clock_in_time, clock_out_time)
        
        # 根据班制类型判断考勤状态
        if shift_type == "12H_DAY":  # 12小时白班
            return self._check_12h_day_shift(clock_in_time, clock_out_time)
        elif shift_type == "8H":  # 8小时班
            return self._check_8h_shift(clock_in_time, clock_out_time)
        elif shift_type == "12H_NIGHT":  # 12小时夜班
            return self._check_12h_night_shift(clock_in_time, clock_out_time)
        else:
            # 无法识别班制，使用通用判断
            return "班制未识别"
    
    def _identify_shift_type(self, clock_in_time: datetime, clock_out_time: datetime) -> str:
        """
        根据打卡时间识别班制类型
        优化后的班制识别逻辑，更准确地区分不同班制
        """
        in_hour = clock_in_time.hour
        in_minute = clock_in_time.minute
        out_hour = clock_out_time.hour
        out_minute = clock_out_time.minute
        
        # 计算工作时长（小时）
        work_duration = (clock_out_time - clock_in_time).total_seconds() / 3600
        
        # 12小时夜班：上班时间在18:00之后，或者工作时长跨夜（下班时间在次日上午）
        if in_hour >= 18 or (in_hour < 12 and out_hour < 12 and work_duration > 10):
            return "12H_NIGHT"
        
        # 8小时班：上班时间在8:00-10:00之间，下班时间在16:00-18:30之间，工作时长7-9小时
        elif (8 <= in_hour <= 10) and (16 <= out_hour <= 18) and (7 <= work_duration <= 9):
            return "8H"
        
        # 12小时白班：上班时间在6:00-8:00之间，或工作时长10小时以上
        elif (6 <= in_hour <= 8) or work_duration >= 10:
            return "12H_DAY"
        
        # 默认按8小时班处理
        else:
            return "8H"
    
    def _check_12h_day_shift(self, clock_in_time: datetime, clock_out_time: datetime) -> str:
        """
        检查12小时白班考勤状态 (7:00-19:00)
        迟到线：7:30，早退线：19:00
        弹性工作规则：如果员工早到，可以提前下班，但工作时长必须>=12小时
        """
        # 计算工作时长（小时）
        work_duration = (clock_out_time - clock_in_time).total_seconds() / 3600
        
        # 迟到判断：7:30之后
        is_late = (clock_in_time.hour > 7) or (clock_in_time.hour == 7 and clock_in_time.minute > 30)
        
        # 早退判断：19:00之前
        is_early = clock_out_time.hour < 19
        
        # 弹性工作时间判断：如果工作时长>=12小时，即使提前下班也算正常
        if is_early and work_duration >= 12:
            is_early = False  # 满足工作时长要求，不算早退
        
        if is_late and is_early:
            return "迟到早退"
        elif is_late:
            return "迟到"
        elif is_early:
            return "早退"
        else:
            return "正常"
    
    def _check_8h_shift(self, clock_in_time: datetime, clock_out_time: datetime) -> str:
        """
        检查8小时班考勤状态 (8:45-17:15)
        迟到线：9:00，早退线：17:15
        弹性工作规则：如果员工早到，可以提前下班，但工作时长必须>=8小时
        """
        # 计算工作时长（小时）
        work_duration = (clock_out_time - clock_in_time).total_seconds() / 3600
        
        # 迟到判断：9:00之后
        is_late = (clock_in_time.hour > 9) or (clock_in_time.hour == 9 and clock_in_time.minute > 0)
        
        # 早退判断：17:15之前
        is_early = (clock_out_time.hour < 17) or (clock_out_time.hour == 17 and clock_out_time.minute < 15)
        
        # 弹性工作时间判断：如果工作时长>=8小时，即使提前下班也算正常
        if is_early and work_duration >= 8:
            is_early = False  # 满足工作时长要求，不算早退
        
        if is_late and is_early:
            return "迟到早退"
        elif is_late:
            return "迟到"
        elif is_early:
            return "早退"
        else:
            return "正常"
    
    def _check_12h_night_shift(self, clock_in_time: datetime, clock_out_time: datetime) -> str:
        """
        检查12小时夜班考勤状态 (19:00-7:00)
        迟到线：19:30，早退线：7:00
        弹性工作规则：如果员工早到，可以提前下班，但工作时长必须>=12小时
        """
        # 计算工作时长（小时）- 夜班需要考虑跨日期
        if clock_out_time < clock_in_time:  # 跨日期情况
            work_duration = (clock_out_time + timedelta(days=1) - clock_in_time).total_seconds() / 3600
        else:
            work_duration = (clock_out_time - clock_in_time).total_seconds() / 3600
        
        # 夜班迟到判断：19:30之后
        is_late = False
        if clock_in_time.hour > 19 or (clock_in_time.hour == 19 and clock_in_time.minute > 30):
            is_late = True
        
        # 夜班早退判断：7:00之前（需要考虑跨日期）
        is_early = False
        if clock_out_time.hour < 7:
            is_early = True
        
        # 弹性工作时间判断：如果工作时长>=12小时，即使提前下班也算正常
        if is_early and work_duration >= 12:
            is_early = False  # 满足工作时长要求，不算早退
        
        if is_late and is_early:
            return "迟到早退"
        elif is_late:
            return "迟到"
        elif is_early:
            return "早退"
        else:
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
        try:
            logger.info("开始测试MSSQL数据库连接")
            connection_result = self.mssql_conn.test_connection()
            
            if connection_result:
                logger.info("MSSQL数据库连接测试成功")
            else:
                logger.error("MSSQL数据库连接测试失败")
                
            return connection_result
            
        except Exception as e:
            logger.error(f"MSSQL连接测试异常: {str(e)}")
            return False
    
    def start_background_sync(self, sync_interval_minutes: int = None):
        """
        启动后台定时同步服务
        
        Args:
            sync_interval_minutes: 同步间隔（分钟），如果不指定则使用环境配置的默认值
        """
        if self._is_running:
            logger.warning("后台同步服务已在运行中")
            return
        
        # 如果指定了同步间隔，则使用指定值；否则使用已初始化的环境配置值
        if sync_interval_minutes is not None:
            self._sync_interval = sync_interval_minutes * 60
            interval_source = "参数指定"
        else:
            # 使用已经根据环境配置初始化的值
            interval_source = "环境配置"
        
        self._is_running = True
        self._stop_event.clear()
        self._sync_status = "running"
        
        # 启动后台线程
        self._background_sync_thread = threading.Thread(
            target=self._background_sync_loop,
            daemon=True,
            name="MSSQLBackgroundSync"
        )
        self._background_sync_thread.start()
        
        actual_minutes = self._sync_interval // 60
        logger.info(f"后台同步服务已启动，同步间隔: {actual_minutes} 分钟 (来源: {interval_source})")
    
    def stop_background_sync(self):
        """
        停止后台定时同步服务
        """
        if not self._is_running:
            logger.warning("后台同步服务未在运行")
            return
        
        self._is_running = False
        self._stop_event.set()
        self._sync_status = "stopping"
        
        # 等待线程结束
        if self._background_sync_thread and self._background_sync_thread.is_alive():
            self._background_sync_thread.join(timeout=5)
        
        self._sync_status = "stopped"
        logger.info("后台同步服务已停止")
    
    def get_background_sync_status(self) -> Dict:
        """
        获取后台同步服务状态
        
        Returns:
            包含同步状态信息的字典
        """
        return {
            "is_running": self._is_running,
            "status": self._sync_status,
            "sync_interval_minutes": self._sync_interval // 60,
            "last_sync_time": self._last_sync_time.isoformat() if self._last_sync_time else None,
            "thread_alive": self._background_sync_thread.is_alive() if self._background_sync_thread else False,
            "metrics": self._metrics.get_metrics(),
            "health_status": self._get_health_status()
        }
    
    def _classify_error(self, error: Exception) -> SyncErrorType:
        """
        分类错误类型
        """
        error_str = str(error).lower()
        
        if "connection" in error_str or "connect" in error_str:
            return SyncErrorType.CONNECTION_ERROR
        elif "timeout" in error_str:
            return SyncErrorType.TIMEOUT_ERROR
        elif "permission" in error_str or "access" in error_str or "denied" in error_str:
            return SyncErrorType.PERMISSION_ERROR
        elif "data" in error_str or "invalid" in error_str or "format" in error_str:
            return SyncErrorType.DATA_ERROR
        else:
            return SyncErrorType.UNKNOWN_ERROR
    
    def _get_retry_delay(self, error_type: SyncErrorType) -> int:
        """
        根据错误类型获取重试延迟时间
        """
        base_delay = self._retry_delay
        
        if error_type == SyncErrorType.CONNECTION_ERROR:
            return base_delay * 2  # 连接错误延迟更长
        elif error_type == SyncErrorType.TIMEOUT_ERROR:
            return base_delay
        elif error_type == SyncErrorType.PERMISSION_ERROR:
            return base_delay * 3  # 权限错误延迟最长
        else:
            return base_delay
    
    def _check_and_send_alert(self):
        """
        检查是否需要发送告警
        """
        # 连续失败超过阈值时发送告警
        if self._metrics.consecutive_failures >= 3:
            logger.warning(f"同步服务连续失败 {self._metrics.consecutive_failures} 次，需要关注！")
            # 这里可以集成邮件、短信等告警方式
            
        # 错误率过高时发送告警
        if self._metrics.total_syncs > 10:
            error_rate = (self._metrics.failed_syncs / self._metrics.total_syncs) * 100
            if error_rate > 50:
                logger.warning(f"同步服务错误率过高: {error_rate:.2f}%，需要检查！")
    
    def _get_health_status(self) -> Dict:
        """
        获取健康状态
        """
        if not self._health_check_enabled:
            return {"status": "disabled", "message": "健康检查已禁用"}
        
        # 检查连续失败次数
        if self._metrics.consecutive_failures >= 5:
            return {"status": "critical", "message": "连续失败次数过多"}
        elif self._metrics.consecutive_failures >= 3:
            return {"status": "warning", "message": "连续失败次数较多"}
        
        # 检查错误率
        if self._metrics.total_syncs > 5:
            error_rate = (self._metrics.failed_syncs / self._metrics.total_syncs) * 100
            if error_rate > 30:
                return {"status": "warning", "message": f"错误率较高: {error_rate:.2f}%"}
        
        # 检查最后同步时间
        if self._last_sync_time:
            time_since_last = datetime.now() - self._last_sync_time
            if time_since_last.total_seconds() > self._sync_interval * 2:
                return {"status": "warning", "message": "同步延迟过长"}
        
        return {"status": "healthy", "message": "服务运行正常"}
    
    def get_sync_metrics(self) -> Dict:
        """
        获取同步监控指标
        """
        return self._metrics.get_metrics()
    
    def _get_environment_name(self) -> str:
        """
        获取当前环境名称
        """
        # 检查环境变量
        env = os.getenv('ENVIRONMENT', '').lower()
        if env in ['development', 'dev']:
            return 'development'
        elif env in ['production', 'prod']:
            return 'production'
        elif env in ['testing', 'test']:
            return 'testing'
        
        # 检查其他常见的环境变量
        if os.getenv('DEBUG', '').lower() in ['true', '1']:
            return 'development'
        
        # 默认为开发环境
        return 'development'
    
    def _get_sync_interval_by_env(self) -> int:
        """
        根据环境获取同步间隔（秒）
        """
        env_name = self._get_environment_name()
        
        # 检查是否有自定义的同步间隔环境变量
        custom_interval = os.getenv('SYNC_INTERVAL_MINUTES')
        if custom_interval:
            try:
                return int(custom_interval) * 60
            except ValueError:
                logger.warning(f"无效的SYNC_INTERVAL_MINUTES值: {custom_interval}，使用默认值")
        
        # 根据环境设置默认间隔
        if env_name == 'development':
            return 1 * 60  # 开发环境：1分钟
        elif env_name == 'testing':
            return 2 * 60  # 测试环境：2分钟
        else:
            return 5 * 60  # 生产环境：5分钟
    
    def update_sync_interval(self, interval_minutes: int) -> Dict:
        """
        动态更新同步间隔
        """
        if interval_minutes < 1:
            raise ValueError("同步间隔不能小于1分钟")
        
        old_interval = self._sync_interval // 60
        self._sync_interval = interval_minutes * 60
        
        logger.info(f"同步间隔已更新: {old_interval}分钟 -> {interval_minutes}分钟")
        
        return {
            "message": f"同步间隔已更新为 {interval_minutes} 分钟",
            "old_interval_minutes": old_interval,
            "new_interval_minutes": interval_minutes,
            "requires_restart": self._is_running
        }
    
    def _background_sync_loop(self):
        """
        后台同步循环
        """
        logger.info("后台同步循环已启动")
        
        while self._is_running and not self._stop_event.is_set():
            try:
                # 执行同步操作
                self._perform_background_sync()
                
                # 更新最后同步时间
                self._last_sync_time = datetime.now()
                
                # 等待下次同步
                if self._stop_event.wait(timeout=self._sync_interval):
                    # 如果收到停止信号，退出循环
                    break
                    
            except Exception as e:
                error_type = self._classify_error(e)
                self._metrics.record_sync_failure(error_type, str(e))
                
                logger.error(f"后台同步过程中发生错误 [{error_type.value}]: {str(e)}")
                logger.error(f"错误详情: {traceback.format_exc()}")
                
                # 检查是否需要告警
                self._check_and_send_alert()
                
                # 根据错误类型决定重试策略
                retry_delay = self._get_retry_delay(error_type)
                logger.info(f"将在 {retry_delay} 秒后重试")
                
                if self._stop_event.wait(timeout=retry_delay):
                    break
        
        logger.info("后台同步循环已结束")
    
    def _perform_background_sync(self):
        """
        执行后台同步操作（增量同步）
        """
        from database.database import get_db
        
        self._metrics.record_sync_start()
        logger.info("开始执行后台增量同步")
        
        try:
            # 获取数据库会话
            db = next(get_db())
            
            try:
                # 获取上次同步时间，如果没有则同步最近3天的数据
                if self._last_sync_time:
                    # 增量同步：从上次同步时间开始
                    sync_days = (datetime.now().date() - self._last_sync_time.date()).days + 1
                    sync_days = max(1, min(sync_days, 3))  # 限制在1-3天之间
                    logger.info(f"执行增量同步，同步最近 {sync_days} 天的数据")
                else:
                    # 首次同步：同步最近3天的数据
                    sync_days = 3
                    logger.info(f"首次同步，同步最近 {sync_days} 天的数据")
                
                # 执行同步
                result = self.sync_attendance_records(
                    db=db,
                    sync_date=None,  # 不指定日期，使用默认逻辑
                    employee_nos=None,  # 同步所有员工
                    sync_days=sync_days  # 动态确定同步天数
                )
                
                # 记录成功指标
                records_count = result.get('records_count', 0)
                self._metrics.record_sync_success(records_count)
                self._sync_status = "success"
                
                logger.info(f"后台增量同步完成: {result.get('message', '未知结果')}，处理记录数: {records_count}")
                
            finally:
                db.close()
                
        except Exception as e:
            self._sync_status = "error"
            logger.error(f"后台增量同步执行失败: {str(e)}")
            raise

# 全局同步服务实例
mssql_sync_service = MSSQLSyncService()