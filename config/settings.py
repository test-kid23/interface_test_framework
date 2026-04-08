# 全局常量配置
import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 配置文件路径
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
ENV_CONFIG_PATH = os.path.join(CONFIG_DIR, 'env.yaml')

# 数据文件路径
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
GLOBAL_DATA_PATH = os.path.join(DATA_DIR, 'global_data.yaml')

# 日志配置
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_LEVEL = 'DEBUG'

# 报告配置
REPORT_DIR = os.path.join(PROJECT_ROOT, 'reports')
ALLURE_RESULTS_DIR = os.path.join(REPORT_DIR, 'allure_results')
ALLURE_HTML_DIR = os.path.join(REPORT_DIR, 'allure_html')
