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
        # 这里使用示例配置，实际使用时需要配置真实的MSSQL服务器信息
        server = getattr(settings, 'MSSQL_SERVER', 'localhost')
        database = getattr(settings, 'MSSQL_DATABASE', 'AttendanceDB')
        username = getattr(settings, 'MSSQL_USERNAME', 'sa')
        password = getattr(settings, 'MSSQL_PASSWORD', 'password')
        driver = getattr(settings, 'MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server')
        
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "TrustServerCertificate=yes;"
        )
        
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
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
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
            
            cursor.close()
            return result
            
        except Exception as e:
            logger.error(f"执行查询失败: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            return False

# 全局MSSQL连接实例
mssql_conn = MSSQLConnection()

def get_mssql_connection() -> MSSQLConnection:
    """
    获取MSSQL连接实例
    """
    return mssql_conn