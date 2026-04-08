import argparse
import pytest
import os
from libs.env_manager import env_manager
from config.settings import ALLURE_RESULTS_DIR, ALLURE_HTML_DIR
from libs.logger import logger

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="接口自动化测试执行器")
    parser.add_argument('--env', type=str, help='指定环境（test/prod）')
    parser.add_argument('--mark', type=str, help='执行特定标记的用例')
    parser.add_argument('--data', type=str, help='指定单个YAML文件')
    parser.add_argument('--generate-report', action='store_true', help='生成Allure HTML报告')
    return parser.parse_args()

def main():
    """主执行函数"""
    args = parse_args()
    
    # 设置环境
    if args.env:
        env_manager.set_active_env(args.env)
    
    # 构建pytest命令参数
    pytest_args = [
        "tests/test_runner.py",
        f"--alluredir={ALLURE_RESULTS_DIR}",
        "--clean-alluredir"
    ]
    
    # 添加标记过滤
    if args.mark:
        pytest_args.extend(["-m", args.mark])
    
    # 添加数据文件过滤（简单匹配）
    if args.data:
        pytest_args.extend(["-k", args.data])
    
    logger.info(f"开始执行测试，参数: {pytest_args}")
    
    # 执行测试
    try:
        result = pytest.main(pytest_args)
        logger.info(f"测试执行完成，结果: {result}")
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        return 1
    
    # 生成HTML报告
    if args.generate_report:
        logger.info("开始生成Allure HTML报告")
        try:
            os.system(f"allure generate {ALLURE_RESULTS_DIR} -o {ALLURE_HTML_DIR} --clean")
            logger.info(f"Allure HTML报告已生成: {ALLURE_HTML_DIR}")
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
    
    return result

if __name__ == "__main__":
    exit(main())
