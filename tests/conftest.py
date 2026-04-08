import pytest
import allure
from libs.env_manager import env_manager
from libs.request_client import RequestClient
from libs.db_client import db_client
from libs.variable_substitution import VariableContext
from libs.logger import logger

@pytest.fixture(scope="session")
def env():
    """环境配置 fixture"""
    return env_manager

@pytest.fixture(scope="session")
def http_client():
    """HTTP客户端 fixture"""
    client = RequestClient()
    yield client
    client.close()

@pytest.fixture(scope="session")
def db_client():
    """数据库客户端 fixture"""
    yield db_client
    db_client.close()

@pytest.fixture(scope="function")
def variable_context():
    """变量上下文 fixture，每个用例独立"""
    return VariableContext()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """在失败时自动附加日志"""
    # 执行测试
    outcome = yield
    report = outcome.get_result()
    
    # 当测试失败时
    if report.when == "call" and report.failed:
        # 可以在这里添加更多的附件，例如请求/响应信息
        logger.error(f"测试失败: {item.name}")
        # 注意：实际的请求/响应信息已经在 RequestClient 中通过 Allure 步骤附加了
