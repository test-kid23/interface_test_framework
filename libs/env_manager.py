import yaml
import os
from config.settings import ENV_CONFIG_PATH
from libs.logger import logger

class EnvManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnvManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载环境配置文件"""
        try:
            with open(ENV_CONFIG_PATH, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self._active_env = self.config.get('active', 'test')
            logger.info(f"环境配置加载成功，当前环境: {self._active_env}")
        except Exception as e:
            logger.error(f"加载环境配置失败: {e}")
            raise
    
    def set_active_env(self, env_name):
        """设置当前环境"""
        if env_name in self.config.get('environments', {}):
            self._active_env = env_name
            logger.info(f"环境切换成功: {env_name}")
        else:
            logger.warning(f"环境 {env_name} 不存在，使用默认环境: {self._active_env}")
    
    def get_active_env(self):
        """返回当前环境名称"""
        return self._active_env
    
    def get_base_url(self):
        """返回当前环境的 base_url"""
        return self.config.get('environments', {}).get(self._active_env, {}).get('base_url', '')
    
    def get_db_config(self):
        """返回当前环境的数据库配置"""
        return self.config.get('environments', {}).get(self._active_env, {}).get('database', {})
    
    def get_headers(self):
        """返回当前环境的公共请求头"""
        return self.config.get('environments', {}).get(self._active_env, {}).get('headers', {})
    
    def get_timeout(self):
        """返回当前环境的超时设置"""
        return self.config.get('environments', {}).get(self._active_env, {}).get('timeout', 30)

# 导出单例实例
env_manager = EnvManager()
__all__ = ["env_manager"]
