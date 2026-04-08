import jsonpath
from libs.logger import logger
from libs.db_client import db_client

class AssertUtil:
    """断言工具类"""
    
    @staticmethod
    def assert_eq(actual, expected, message=None):
        """断言相等"""
        assert actual == expected, message or f"断言失败: 期望 {expected}, 实际 {actual}"
        logger.info(f"断言成功: {actual} == {expected}")
    
    @staticmethod
    def assert_contains(actual, expected, message=None):
        """断言包含"""
        assert expected in actual, message or f"断言失败: {actual} 不包含 {expected}"
        logger.info(f"断言成功: {actual} 包含 {expected}")
    
    @staticmethod
    def assert_gt(actual, expected, message=None):
        """断言大于"""
        assert actual > expected, message or f"断言失败: {actual} 不大于 {expected}"
        logger.info(f"断言成功: {actual} > {expected}")
    
    @staticmethod
    def assert_gte(actual, expected, message=None):
        """断言大于等于"""
        assert actual >= expected, message or f"断言失败: {actual} 不大于等于 {expected}"
        logger.info(f"断言成功: {actual} >= {expected}")
    
    @staticmethod
    def assert_lt(actual, expected, message=None):
        """断言小于"""
        assert actual < expected, message or f"断言失败: {actual} 不小于 {expected}"
        logger.info(f"断言成功: {actual} < {expected}")
    
    @staticmethod
    def assert_lte(actual, expected, message=None):
        """断言小于等于"""
        assert actual <= expected, message or f"断言失败: {actual} 不小于等于 {expected}"
        logger.info(f"断言成功: {actual} <= {expected}")
    
    @staticmethod
    def assert_not_none(actual, message=None):
        """断言不为None"""
        assert actual is not None, message or "断言失败: 值为None"
        logger.info(f"断言成功: {actual} 不为None")
    
    @staticmethod
    def assert_jsonpath(response, jsonpath_expr, expected, message=None):
        """使用JSONPath断言响应"""
        try:
            response_json = response.json()
            actual = jsonpath.jsonpath(response_json, jsonpath_expr)
            if actual:
                actual = actual[0] if len(actual) == 1 else actual
            else:
                actual = None
            AssertUtil.assert_eq(actual, expected, message)
        except Exception as e:
            logger.error(f"JSONPath断言失败: {e}")
            raise
    
    @staticmethod
    def assert_status_code(response, expected_status_code, message=None):
        """断言响应状态码"""
        AssertUtil.assert_eq(response.status_code, expected_status_code, message)
    
    @staticmethod
    def assert_db_query(sql, expected, message=None):
        """断言数据库查询结果"""
        try:
            result = db_client.execute(sql)
            # 解析预期表达式，如 "record_count >= 1"
            if isinstance(expected, str) and '>=' in expected:
                parts = expected.split('>=')
                if parts[0].strip() == 'record_count':
                    count = len(result)
                    expected_count = int(parts[1].strip())
                    AssertUtil.assert_gte(count, expected_count, message)
            elif isinstance(expected, str) and '==' in expected:
                parts = expected.split('==')
                if parts[0].strip() == 'record_count':
                    count = len(result)
                    expected_count = int(parts[1].strip())
                    AssertUtil.assert_eq(count, expected_count, message)
            else:
                # 直接比较结果
                AssertUtil.assert_eq(result, expected, message)
        except Exception as e:
            logger.error(f"数据库断言失败: {e}")
            raise

# 导出类
__all__ = ["AssertUtil"]
