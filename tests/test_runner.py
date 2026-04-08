import os
import json
import pytest
import allure
from libs.yaml_loader import YamlLoader
from libs.assert_util import AssertUtil
from libs.logger import logger

# 加载所有用例
case_list = YamlLoader.load_yaml_files()

# 动态生成测试函数
for case in case_list:
    # 生成测试函数名
    func_name = f"test_{case['module']}_{case['name'].replace(' ', '_').lower()}"
    
    # 定义测试函数
    def create_test_func(case_data):
        def test_func(http_client, variable_context):
            logger.info(f"开始执行测试用例: {case_data['name']}")
            
            # 1. 初始化变量上下文（加载局部 variables）
            variable_context.update_from_dict(case_data['variables'])
            logger.debug(f"变量上下文初始化完成: {variable_context.variables}")
            
            # 2. 发送请求前，对 request 数据进行变量替换
            request_data = variable_context.substitute(case_data['request'])
            logger.debug(f"请求数据变量替换完成: {json.dumps(request_data, indent=2)}")
            
            # 3. 发送请求
            method = request_data.get('method', 'GET')
            url = request_data.get('url')
            headers = request_data.get('headers', {})
            json_data = request_data.get('json')
            data = request_data.get('data')
            
            response = http_client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                data=data
            )
            
            # 4. 提取响应数据到变量上下文
            extract = case_data.get('extract', [])
            if extract:
                try:
                    response_json = response.json()
                    for item in extract:
                        for key, value in item.items():
                            # 处理 jsonpath 表达式
                            if value.startswith('jsonpath '):
                                jsonpath_expr = value.replace('jsonpath ', '')
                                import jsonpath
                                extracted_value = jsonpath.jsonpath(response_json, jsonpath_expr)
                                if extracted_value:
                                    extracted_value = extracted_value[0] if len(extracted_value) == 1 else extracted_value
                                    variable_context.update(key, extracted_value)
                                    logger.info(f"提取变量成功: {key} = {extracted_value}")
                except Exception as e:
                    logger.error(f"提取变量失败: {e}")
            
            # 5. 执行断言（validate）
            validate = case_data.get('validate', [])
            if validate:
                for item in validate:
                    for assert_type, assert_args in item.items():
                        if assert_type == 'eq':
                            if assert_args[0] == 'status_code':
                                AssertUtil.assert_status_code(response, assert_args[1])
                            elif assert_args[0].startswith('jsonpath '):
                                jsonpath_expr = assert_args[0].replace('jsonpath ', '')
                                AssertUtil.assert_jsonpath(response, jsonpath_expr, assert_args[1])
                        elif assert_type == 'contains':
                            if assert_args[0].startswith('jsonpath '):
                                jsonpath_expr = assert_args[0].replace('jsonpath ', '')
                                import jsonpath
                                actual = jsonpath.jsonpath(response.json(), jsonpath_expr)
                                if actual:
                                    actual = actual[0] if len(actual) == 1 else actual
                                    AssertUtil.assert_contains(str(actual), assert_args[1])
            
            # 6. 执行数据库断言（db_validate）
            db_validate = case_data.get('db_validate', [])
            if db_validate:
                for item in db_validate:
                    sql = variable_context.substitute(item.get('sql'))
                    expect = item.get('expect')
                    AssertUtil.assert_db_query(sql, expect)
            
            logger.info(f"测试用例执行成功: {case_data['name']}")
        
        # 添加标记
        for marker in case_data['markers']:
            test_func = getattr(pytest.mark, marker)(test_func)
        
        # 设置函数文档
        test_func.__doc__ = f"{case_data['description'] or ''} - {case_data['name']}"
        
        return test_func
    
    # 创建测试函数
    test_func = create_test_func(case)
    
    # 重命名函数
    test_func.__name__ = func_name
    
    # 添加到当前模块
    globals()[func_name] = test_func

# 清理临时变量
del case_list
