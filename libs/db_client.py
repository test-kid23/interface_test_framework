import pymysql
import time
from libs.env_manager import env_manager
from libs.logger import logger

class DBClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBClient, cls).__new__(cls)
            cls._instance._init_connection()
        return cls._instance
    
    def _init_connection(self):
        """初始化数据库连接"""
        self.db_config = env_manager.get_db_config()
        self.connection = None
    
    def _get_connection(self):
        """获取数据库连接"""
        if not self.connection or not self._is_connected():
            try:
                self.connection = pymysql.connect(
                    host=self.db_config.get('host'),
                    port=self.db_config.get('port', 3306),
                    user=self.db_config.get('user'),
                    password=self.db_config.get('password'),
                    db=self.db_config.get('db'),
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )
                logger.info(f"数据库连接成功: {self.db_config.get('host')}:{self.db_config.get('port')}/{self.db_config.get('db')}")
            except Exception as e:
                logger.error(f"数据库连接失败: {e}")
                raise
        return self.connection
    
    def _is_connected(self):
        """检查连接是否有效"""
        try:
            if self.connection:
                self.connection.ping()
                return True
        except:
            pass
        return False
    
    def execute(self, sql, params=None):
        """执行查询，返回 List[Dict]"""
        start_time = time.time()
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                logger.debug(f"执行SQL: {sql}, 参数: {params}")
                cursor.execute(sql, params)
                result = cursor.fetchall()
                logger.info(f"SQL执行成功，返回 {len(result)} 条记录，耗时: {time.time() - start_time:.3f}s")
                return result
        except Exception as e:
            logger.error(f"SQL执行失败: {e}, SQL: {sql}, 参数: {params}")
            raise
    
    def execute_many(self, sql, params_list):
        """批量执行"""
        start_time = time.time()
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                logger.debug(f"批量执行SQL: {sql}, 参数数量: {len(params_list)}")
                cursor.executemany(sql, params_list)
                connection.commit()
                logger.info(f"批量SQL执行成功，影响行数: {cursor.rowcount}, 耗时: {time.time() - start_time:.3f}s")
                return cursor.rowcount
        except Exception as e:
            connection.rollback()
            logger.error(f"批量SQL执行失败: {e}, SQL: {sql}")
            raise
    
    def execute_commit(self, sql, params=None):
        """执行更新/插入，返回影响行数"""
        start_time = time.time()
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                logger.debug(f"执行更新SQL: {sql}, 参数: {params}")
                cursor.execute(sql, params)
                connection.commit()
                logger.info(f"更新SQL执行成功，影响行数: {cursor.rowcount}, 耗时: {time.time() - start_time:.3f}s")
                return cursor.rowcount
        except Exception as e:
            connection.rollback()
            logger.error(f"更新SQL执行失败: {e}, SQL: {sql}, 参数: {params}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("数据库连接已关闭")
            except Exception as e:
                logger.error(f"关闭数据库连接失败: {e}")

# 导出单例实例
db_client = DBClient()
__all__ = ["db_client"]
