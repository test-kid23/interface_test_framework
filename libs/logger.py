from loguru import logger
import sys
import os
from config.settings import LOG_DIR, LOG_LEVEL

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

# 移除默认处理器
logger.remove()

# 配置控制台输出（INFO级别，彩色格式）
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{level}</level> <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# 配置文件输出（DEBUG级别，按天轮转，保留7天）
logger.add(
    os.path.join(LOG_DIR, "interface_test_{time:YYYY-MM-DD}.log"),
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} {level} {name}:{function}:{line} - {message}"
)

# 导出全局logger对象
__all__ = ["logger"]
