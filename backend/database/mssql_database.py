import pyodbc
from typing import Optional
from config.config import settings
import logging

logger = logging.getLogger(__name__)

class MSSQLConnection:
    """
    MSSQL数据库连接管理类
    """
    
    def __init__(self):
        self.connection_string = self._build_connection_string()
        self.connection: Optional[pyodbc.Connection] = None
    
    def _build_connection_string(self) -> str:
        """
        构建MSSQL连接字符串
        """
        # 从环境变量或配置中获取MSSQL连接参数
        server = getattr(settings, 'MSSQL_SERVER', 'localhost')
        database = getattr(settings, 'MSSQL_DATABASE', 'AttendanceDB')
        username = getattr(settings, 'MSSQL_USERNAME', 'sa')
        password = getattr(settings, 'MSSQL_PASSWORD', 'password')
        driver = getattr(settings, 'MSSQL_DRIVER', 'ODBC Driver 18 for SQL Server')
        
        # 构建连接字符串，添加更多兼容性选项
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "TrustServerCertificate=yes;"
            "Encrypt=no;"
            "Connection Timeout=30;"
            "Command Timeout=60;"
        )
        
        logger.info(f"MSSQL连接字符串: {connection_string.replace(password, '***')}")
        return connection_string
    
    def connect(self) -> pyodbc.Connection:
        """
        建立MSSQL数据库连接
        """
        try:
            if self.connection is None or self.connection.closed:
                self.connection = pyodbc.connect(self.connection_string)
                logger.info("MSSQL数据库连接成功")
            return self.connection
        except Exception as e:
            logger.error(f"MSSQL数据库连接失败: {str(e)}")
            raise
    
    def disconnect(self):
        """
        关闭MSSQL数据库连接
        """
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.connection = None
            logger.info("MSSQL数据库连接已关闭")
    
    def execute_query(self, query: str, params: tuple = None):
        """
        执行查询语句
        """
        connection = None
        cursor = None
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 每次查询都创建新的连接，避免连接冲突
                logger.debug(f"尝试连接MSSQL数据库 (第{retry_count + 1}次)")
                connection = pyodbc.connect(self.connection_string)
                cursor = connection.cursor()
                
                logger.debug(f"执行查询: {query[:100]}...")
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # 获取列名
                columns = [column[0] for column in cursor.description] if cursor.description else []
                
                # 获取数据
                rows = cursor.fetchall()
                
                # 转换为字典列表
                result = []
                for row in rows:
                    result.append(dict(zip(columns, row)))
                
                logger.debug(f"查询成功，返回 {len(result)} 条记录")
                return result
                
            except pyodbc.Error as e:
                retry_count += 1
                error_msg = f"MSSQL查询失败 (第{retry_count}次尝试): {str(e)}"
                logger.error(error_msg)
                
                if retry_count >= max_retries:
                    logger.error(f"MSSQL查询失败，已重试{max_retries}次，放弃连接")
                    raise Exception(f"MSSQL数据库连接失败: {str(e)}")
                else:
                    logger.info(f"等待2秒后重试...")
                    import time
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"执行查询时发生未知错误: {str(e)}")
                raise
            finally:
                # 确保资源被正确释放
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        """
        connection = None
        cursor = None
        try:
            logger.info("开始测试MSSQL数据库连接...")
            connection = pyodbc.connect(self.connection_string)
            
            # 执行简单查询验证连接
            cursor = connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            if result and result[0] == 1:
                logger.info("MSSQL数据库连接测试成功")
                return True
            else:
                logger.error("MSSQL数据库连接测试失败: 查询结果异常")
                return False
                
        except pyodbc.Error as e:
            logger.error(f"MSSQL数据库连接测试失败 (pyodbc错误): {str(e)}")
            return False
        except Exception as e:
            logger.error(f"MSSQL数据库连接测试失败 (未知错误): {str(e)}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# 全局MSSQL连接实例
mssql_conn = MSSQLConnection()

def get_mssql_connection() -> MSSQLConnection:
    """
    获取MSSQL连接实例
    """
    return mssql_conn