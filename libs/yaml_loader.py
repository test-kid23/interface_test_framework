import os
import yaml
import pytest
from config.settings import DATA_DIR, GLOBAL_DATA_PATH
from libs.logger import logger

class YamlLoader:
    """YAML用例加载器"""
    
    @staticmethod
    def load_yaml_files(data_dir=None):
        """递归扫描 data/ 下所有 .yaml 文件，返回解析后的用例列表"""
        if data_dir is None:
            data_dir = DATA_DIR
        
        case_list = []
        
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.yaml'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = yaml.safe_load(f)
                            if data:
                                # 解析用例
                                cases = YamlLoader._parse_cases(data, file_path)
                                case_list.extend(cases)
                                logger.info(f"加载YAML文件成功: {file_path}, 解析出 {len(cases)} 个用例")
                    except Exception as e:
                        logger.error(f"加载YAML文件失败: {file_path}, 错误: {e}")
        
        return case_list
    
    @staticmethod
    def _parse_cases(data, file_path):
        """解析单个YAML文件中的用例"""
        cases = []
        module_name = os.path.basename(os.path.dirname(file_path)) or os.path.basename(file_path).replace('.yaml', '')
        
        # 全局变量
        variables = data.get('variables', {})
        # 数据驱动参数
        parameters = data.get('parameters', [])
        # 用例列表
        case_items = data.get('cases', [])
        
        if parameters:
            # 处理数据驱动
            param_combinations = YamlLoader._generate_param_combinations(parameters)
            for param in param_combinations:
                for case_item in case_items:
                    case = {
                        'module': module_name,
                        'name': case_item.get('name'),
                        'description': data.get('description'),
                        'markers': case_item.get('markers', []),
                        'request': case_item.get('request'),
                        'extract': case_item.get('extract', []),
                        'validate': case_item.get('validate', []),
                        'db_validate': case_item.get('db_validate', []),
                        'variables': {**variables, **param},  # 合并全局变量和参数
                        'file_path': file_path
                    }
                    cases.append(case)
        else:
            # 普通用例
            for case_item in case_items:
                case = {
                    'module': module_name,
                    'name': case_item.get('name'),
                    'description': data.get('description'),
                    'markers': case_item.get('markers', []),
                    'request': case_item.get('request'),
                    'extract': case_item.get('extract', []),
                    'validate': case_item.get('validate', []),
                    'db_validate': case_item.get('db_validate', []),
                    'variables': variables,
                    'file_path': file_path
                }
                cases.append(case)
        
        return cases
    
    @staticmethod
    def _generate_param_combinations(parameters):
        """生成参数组合"""
        if not parameters:
            return []
        
        # 简化版参数组合生成，支持列表形式的参数
        # 例如: [{'phone': ['138001', '139001'], 'pwd': ['123', '456']}]
        param_dict = parameters[0]  # 只处理第一个参数字典
        keys = list(param_dict.keys())
        values = [param_dict[key] for key in keys]
        
        # 生成笛卡尔积
        combinations = []
        def backtrack(index, current):
            if index == len(keys):
                combinations.append(dict(zip(keys, current)))
                return
            for value in values[index]:
                backtrack(index + 1, current + [value])
        
        backtrack(0, [])
        return combinations
    
    @staticmethod
    def generate_pytest_items(case_list):
        """动态创建 pytest 测试函数，使用 @pytest.mark.parametrize 实现参数化"""
        test_functions = []
        
        for i, case in enumerate(case_list):
            # 生成测试函数名
            func_name = f"test_{case['module']}_{case['name'].replace(' ', '_').lower()}"
            
            # 构建测试函数
            def create_test_func(case_data):
                def test_func(http_client, variable_context):
                    # 这里会在测试执行时填充具体逻辑
                    pass
                # 添加标记
                for marker in case_data['markers']:
                    test_func = getattr(pytest.mark, marker)(test_func)
                # 设置函数文档
                test_func.__doc__ = f"{case_data['description'] or ''} - {case_data['name']}"
                return test_func
            
            test_func = create_test_func(case)
            test_func.case_data = case  # 存储用例数据
            
            # 重命名函数
            test_func.__name__ = func_name
            test_functions.append(test_func)
        
        return test_functions

# 导出类
__all__ = ["YamlLoader"]
