from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, time, timedelta
import logging

from models import attendance_record as attendance_record_model
from models import exception_rule as exception_rule_model
from models import schedule as schedule_model
from models import employee as employee_model
from services import exception_rule_service
from services import notification_service
from schemas import notification as notification_schema

logger = logging.getLogger(__name__)

class ExceptionDetectionService:
    """
    异常检测服务
    负责根据异常规则检测考勤记录中的异常情况
    """
    
    def __init__(self):
        self.standard_work_start = time(9, 0)  # 标准上班时间 9:00
        self.standard_work_end = time(18, 0)   # 标准下班时间 18:00
    
    def detect_attendance_exceptions(self, db: Session, record_id: Optional[int] = None, 
                                   start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """
        检测考勤异常
        
        Args:
            db: 数据库会话
            record_id: 指定记录ID，如果提供则只检测该记录
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 检测到的异常列表
        """
        try:
            # 获取异常规则
            exception_rules = exception_rule_service.get_exception_rules(db)
            if not exception_rules:
                logger.warning("没有找到异常规则，无法进行异常检测")
                return []
            
            # 获取需要检测的考勤记录
            query = db.query(attendance_record_model.AttendanceRecord)
            
            if record_id:
                query = query.filter(attendance_record_model.AttendanceRecord.record_id == record_id)
            else:
                if start_date:
                    query = query.filter(attendance_record_model.AttendanceRecord.clock_in_time >= start_date)
                if end_date:
                    query = query.filter(attendance_record_model.AttendanceRecord.clock_in_time <= end_date)
            
            records = query.all()
            
            exceptions_found = []
            
            for record in records:
                record_exceptions = self._check_record_exceptions(record, exception_rules)
                if record_exceptions:
                    exceptions_found.extend(record_exceptions)
            
            logger.info(f"异常检测完成，共检测到 {len(exceptions_found)} 个异常")
            return exceptions_found
            
        except Exception as e:
            logger.error(f"异常检测失败: {str(e)}")
            return []
    
    def _check_record_exceptions(self, record: attendance_record_model.AttendanceRecord, 
                               rules: List[exception_rule_model.ExceptionRule]) -> List[Dict]:
        """
        检查单条记录的异常情况
        
        Args:
            record: 考勤记录
            rules: 异常规则列表
            
        Returns:
            List[Dict]: 该记录的异常列表
        """
        exceptions = []
        
        for rule in rules:
            exception = self._apply_rule_to_record(record, rule)
            if exception:
                exceptions.append(exception)
        
        # 检查超出7天的规则
        seven_day_exception = self._check_seven_day_rule(record)
        if seven_day_exception:
            exceptions.append(seven_day_exception)
        
        return exceptions
    
    def _apply_rule_to_record(self, record: attendance_record_model.AttendanceRecord, 
                            rule: exception_rule_model.ExceptionRule) -> Optional[Dict]:
        """
        将规则应用到记录上
        
        Args:
            record: 考勤记录
            rule: 异常规则
            
        Returns:
            Optional[Dict]: 如果发现异常则返回异常信息，否则返回None
        """
        try:
            if rule.rule_type == "迟到":
                return self._check_late_arrival(record, rule)
            elif rule.rule_type == "早退":
                return self._check_early_departure(record, rule)
            elif rule.rule_type == "缺卡":
                return self._check_missing_punch(record, rule)
            elif rule.rule_type == "超期记录":
                return self._check_overdue_record(record, rule)
            else:
                logger.warning(f"未知的规则类型: {rule.rule_type}")
                return None
                
        except Exception as e:
            logger.error(f"应用规则 {rule.rule_name} 到记录 {record.record_id} 时出错: {str(e)}")
            return None
    
    def _check_late_arrival(self, record: attendance_record_model.AttendanceRecord, 
                          rule: exception_rule_model.ExceptionRule) -> Optional[Dict]:
        """
        检查迟到
        """
        if not record.clock_in_time:
            return None
        
        # 计算迟到分钟数
        clock_in_time = record.clock_in_time.time()
        standard_time = self.standard_work_start
        
        if clock_in_time > standard_time:
            # 计算迟到分钟数
            late_minutes = self._calculate_time_difference_minutes(standard_time, clock_in_time)
            
            if late_minutes >= (rule.threshold or 0):
                return {
                    "record_id": record.record_id,
                    "employee_id": record.employee_id,
                    "rule_id": rule.rule_id,
                    "rule_name": rule.rule_name,
                    "exception_type": "迟到",
                    "description": f"迟到 {late_minutes} 分钟，超过阈值 {rule.threshold} 分钟",
                    "severity": "medium" if late_minutes < 30 else "high",
                    "detected_at": datetime.now()
                }
        
        return None
    
    def _check_early_departure(self, record: attendance_record_model.AttendanceRecord, 
                             rule: exception_rule_model.ExceptionRule) -> Optional[Dict]:
        """
        检查早退
        """
        if not record.clock_out_time:
            return None
        
        # 计算早退分钟数
        clock_out_time = record.clock_out_time.time()
        standard_time = self.standard_work_end
        
        if clock_out_time < standard_time:
            # 计算早退分钟数
            early_minutes = self._calculate_time_difference_minutes(clock_out_time, standard_time)
            
            if early_minutes >= (rule.threshold or 0):
                return {
                    "record_id": record.record_id,
                    "employee_id": record.employee_id,
                    "rule_id": rule.rule_id,
                    "rule_name": rule.rule_name,
                    "exception_type": "早退",
                    "description": f"早退 {early_minutes} 分钟，超过阈值 {rule.threshold} 分钟",
                    "severity": "medium" if early_minutes < 30 else "high",
                    "detected_at": datetime.now()
                }
        
        return None
    
    def _check_missing_punch(self, record: attendance_record_model.AttendanceRecord, 
                           rule: exception_rule_model.ExceptionRule) -> Optional[Dict]:
        """
        检查缺卡
        """
        missing_type = None
        
        if not record.clock_in_time and not record.clock_out_time:
            missing_type = "上下班都缺卡"
        elif not record.clock_in_time:
            missing_type = "上班缺卡"
        elif not record.clock_out_time:
            missing_type = "下班缺卡"
        
        if missing_type:
            return {
                "record_id": record.record_id,
                "employee_id": record.employee_id,
                "rule_id": rule.rule_id,
                "rule_name": rule.rule_name,
                "exception_type": "缺卡",
                "description": f"{missing_type}",
                "severity": "high",
                "detected_at": datetime.now()
            }
        
        return None
    
    def _check_overdue_record(self, record: attendance_record_model.AttendanceRecord, 
                            rule: exception_rule_model.ExceptionRule) -> Optional[Dict]:
        """
        检查考勤记录是否超期（基于规则设定的天数阈值）
        
        Args:
            record: 考勤记录
            rule: 超期记录规则
            
        Returns:
            Optional[Dict]: 如果发现超期则返回异常信息，否则返回None
        """
        if not record.clock_in_time:
            return None
        
        # 计算记录日期与当前日期的差值
        record_date = record.clock_in_time.date()
        current_date = datetime.now().date()
        days_diff = abs((current_date - record_date).days)
        
        # rule.threshold 现在表示天数
        threshold_days = rule.threshold
        
        if days_diff > threshold_days:
            return {
                "record_id": record.record_id,
                "employee_id": record.employee_id,
                "rule_id": rule.rule_id,
                "rule_name": rule.rule_name,
                "exception_type": "超期记录",
                "description": f"考勤记录日期 {record_date} 距离当前日期超过{threshold_days}天 (实际{days_diff}天)",
                "severity": "medium",
                "detected_at": datetime.now()
            }
        
        return None
    
    def _check_seven_day_rule(self, record: attendance_record_model.AttendanceRecord) -> Optional[Dict]:
        """
        检查考勤记录或排班是否超出7天（保留作为默认规则）
        """
        if not record.clock_in_time:
            return None
        
        # 计算记录日期与当前日期的差值
        record_date = record.clock_in_time.date()
        current_date = datetime.now().date()
        days_diff = abs((current_date - record_date).days)
        
        if days_diff > 7:
            return {
                "record_id": record.record_id,
                "employee_id": record.employee_id,
                "rule_id": None,  # 这是默认规则，没有对应的rule_id
                "rule_name": "默认7天规则",
                "exception_type": "超期记录",
                "description": f"考勤记录日期 {record_date} 距离当前日期超过7天 ({days_diff}天)",
                "severity": "medium",
                "detected_at": datetime.now()
            }
        
        return None
    
    def _calculate_time_difference_minutes(self, time1: time, time2: time) -> int:
        """
        计算两个时间之间的分钟差
        
        Args:
            time1: 较早的时间
            time2: 较晚的时间
            
        Returns:
            int: 分钟差
        """
        # 将时间转换为分钟数
        minutes1 = time1.hour * 60 + time1.minute
        minutes2 = time2.hour * 60 + time2.minute
        
        return abs(minutes2 - minutes1)
    
    def update_record_status_based_on_exceptions(self, db: Session, record_id: int, exceptions: List[Dict]):
        """
        根据检测到的异常更新记录状态
        
        Args:
            db: 数据库会话
            record_id: 记录ID
            exceptions: 异常列表
        """
        try:
            record = db.query(attendance_record_model.AttendanceRecord).filter(
                attendance_record_model.AttendanceRecord.record_id == record_id
            ).first()
            
            if not record:
                return
            
            if exceptions:
                # 如果有异常，更新状态
                exception_types = [exc["exception_type"] for exc in exceptions]
                
                if "缺卡" in exception_types:
                    record.status = "缺卡"
                elif "迟到" in exception_types and "早退" in exception_types:
                    record.status = "迟到早退"
                elif "迟到" in exception_types:
                    record.status = "迟到"
                elif "早退" in exception_types:
                    record.status = "早退"
                elif "超期记录" in exception_types:
                    record.status = "超期记录"
                else:
                    record.status = "异常"
                
                # 设置处理状态为未处理
                if record.process_status == 'unprocessed':
                    record.process_status = 'unprocessed'
                
                # 发送邮件通知
                self._send_exception_notification(db, record, exceptions)
            else:
                # 没有异常，设置为正常
                record.status = "正常"
            
            db.commit()
            logger.info(f"更新记录 {record_id} 状态为: {record.status}")
            
        except Exception as e:
            logger.error(f"更新记录状态失败: {str(e)}")
            db.rollback()
    
    def _send_exception_notification(self, db: Session, record: attendance_record_model.AttendanceRecord, exceptions: List[Dict]):
        """
        发送异常通知邮件
        
        Args:
            db: 数据库会话
            record: 考勤记录
            exceptions: 异常列表
        """
        try:
            # 获取员工信息
            employee = db.query(employee_model.Employee).filter(
                employee_model.Employee.employee_id == record.employee_id
            ).first()
            
            if not employee or not employee.email:
                logger.warning(f"员工 {record.employee_id} 邮箱信息不存在，无法发送异常通知")
                return
            
            # 构建异常描述
            exception_descriptions = []
            for exc in exceptions:
                exception_descriptions.append(f"- {exc['exception_type']}: {exc['description']}")
            
            # 构建邮件内容
            clock_in_time = record.clock_in_time.strftime('%Y-%m-%d %H:%M:%S') if record.clock_in_time else '未打卡'
            clock_out_time = record.clock_out_time.strftime('%Y-%m-%d %H:%M:%S') if record.clock_out_time else '未打卡'
            
            notification_message = f"""考勤异常通知

员工姓名：{employee.name}
员工工号：{employee.employee_no}
考勤日期：{record.clock_in_time.date() if record.clock_in_time else '未知'}
上班时间：{clock_in_time}
下班时间：{clock_out_time}

检测到的异常：
{chr(10).join(exception_descriptions)}

请及时处理相关异常情况。

此邮件由考勤管理系统自动发送，请勿回复。"""
            
            # 创建通知
            notification = notification_schema.NotificationCreate(
                employee_id=record.employee_id,
                message=notification_message,
                type="exception"
            )
            
            # 发送邮件通知
            result = notification_service.create_notification(db=db, notification=notification)
            
            if result.get("status") == "email_sent":
                logger.info(f"异常通知邮件已发送给员工 {employee.name} ({employee.email})")
            else:
                logger.warning(f"异常通知邮件发送失败: {result.get('message', '未知错误')}")
                
        except Exception as e:
            logger.error(f"发送异常通知邮件失败: {str(e)}")

# 创建全局实例
exception_detection_service = ExceptionDetectionService()