import re
from libs.logger import logger

class VariableContext:
    """变量上下文管理类"""
    
    def __init__(self):
        """初始化变量上下文"""
        self.variables = {}
    
    def get(self, key, default=None):
        """获取变量值"""
        return self.variables.get(key, default)
    
    def update(self, key, value):
        """更新变量值"""
        self.variables[key] = value
        logger.debug(f"变量更新: {key} = {value}")
    
    def update_from_dict(self, data):
        """从字典更新变量"""
        if isinstance(data, dict):
            self.variables.update(data)
            logger.debug(f"从字典更新变量: {list(data.keys())}")
    
    def substitute(self, obj):
        """遍历数据结构替换所有字符串中的变量"""
        return self._substitute_recursive(obj)
    
    def _substitute_recursive(self, obj):
        """递归替换变量"""
        if isinstance(obj, str):
            return self._replace_variables(obj)
        elif isinstance(obj, list):
            return [self._substitute_recursive(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._substitute_recursive(v) for k, v in obj.items()}
        else:
            return obj
    
    def _replace_variables(self, text):
        """替换字符串中的变量"""
        if not isinstance(text, str):
            return text
        
        # 匹配 ${variable_name} 格式的变量
        pattern = r'\$\{([^}]+)\}'
        
        def replace_func(match):
            var_name = match.group(1)
            if var_name in self.variables:
                return str(self.variables[var_name])
            else:
                logger.warning(f"变量 {var_name} 未定义，保持原样")
                return match.group(0)
        
        return re.sub(pattern, replace_func, text)

# 导出类
__all__ = ["VariableContext"]
