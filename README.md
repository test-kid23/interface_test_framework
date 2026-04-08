# 接口自动化测试框架

## 框架目标

- 功能测试工程师通过编写 YAML 文件即可完成接口自动化用例编写
- 支持 RESTful API 和数据库接口（MySQL）的验证
- 支持多环境切换（测试/生产），通过配置文件或命令行参数
- 基于 Pytest 执行，Allure 生成报告，报告中自动包含请求/响应详情
- 提供完整日志系统，便于问题定位
- 代码结构清晰，易于扩展

## 技术栈

- Python 3.8+
- requests
- pytest
- allure-pytest
- pyyaml
- jsonpath
- pymysql
- loguru

## 目录结构

```
interface_test_framework/
├── config/                     # 配置模块
│   ├── settings.py             # 全局常量（路径、日志级别等）
│   └── env.yaml                # 环境配置（base_url、数据库等）
├── data/                       # YAML测试数据（按模块组织）
│   ├── smoke/                  # 冒烟测试用例
│   │   └── login.yaml
│   ├── regression/             # 回归测试用例
│   │   └── order.yaml
│   └── global_data.yaml        # 全局共享数据
├── libs/                       # 核心库
│   ├── env_manager.py          # 环境配置读取与切换
│   ├── yaml_loader.py          # YAML解析与动态生成pytest用例
│   ├── request_client.py       # 封装requests，记录日志与Allure步骤
│   ├── db_client.py            # 数据库操作封装（连接池、SQL执行）
│   ├── assert_util.py          # 断言工具集
│   ├── variable_substitution.py # 变量替换引擎
│   └── logger.py               # 日志初始化
├── utils/                      # 辅助工具
│   └── helper.py               # 通用函数（时间戳、随机数等）
├── tests/                      # Pytest测试目录
│   ├── conftest.py             # Fixtures与钩子
│   └── test_runner.py          # 动态测试生成入口
├── reports/                    # 报告输出
│   ├── allure_results/         # Allure原始数据（自动生成）
│   └── allure_html/            # HTML报告（生成命令输出）
├── logs/                       # 日志文件目录
├── requirements.txt            # 依赖列表
├── pytest.ini                  # Pytest配置
├── run.py                      # 主执行入口
└── README.md                   # 使用手册
```

## 环境配置

1. **修改环境配置**：编辑 `config/env.yaml` 文件，设置 `active` 字段为 `test` 或 `prod`，或在运行时通过 `--env` 参数指定。

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **安装 Allure 命令行工具**（用于生成HTML报告）：
   - 下载 Allure 命令行工具：https://github.com/allure-framework/allure2/releases
   - 将 Allure 安装目录添加到系统环境变量 PATH 中

## 编写用例

在 `data/` 目录下创建 `.yaml` 文件，参考以下模板：

```yaml
name: "登录模块测试"
description: "测试用户登录接口"
variables:                     # 局部变量
  phone: "13800138000"
  pwd: "123456"

cases:
  - name: "正常登录"
    markers: [smoke, p0]      # pytest标记，可选
    request:
      method: POST
      url: "/auth/login"
      headers:
        Content-Type: "application/json"
      json:
        phone: "${phone}"
        password: "${pwd}"
    extract:
      - token: "jsonpath $.data.token"
    validate:
      - eq: ["status_code", 200]
      - eq: ["jsonpath $.code", 0]
      - contains: ["jsonpath $.message", "success"]
    db_validate:
      - sql: "SELECT id FROM user WHERE phone = '${phone}'"
        expect: "record_count >= 1"

  - name: "密码错误"
    request:
      method: POST
      url: "/auth/login"
      json:
        phone: "${phone}"
        password: "wrong"
    validate:
      - eq: ["status_code", 200]
      - eq: ["jsonpath $.code", 40001]
```

### 数据驱动写法

```yaml
name: "登录参数化测试"
parameters:
  - phone: ["13800138000", "13900139000"]
    pwd: ["123456", "654321"]
cases:
  - name: "登录用例"
    request:
      # 请求配置
    validate:
      # 断言配置
```

## 运行测试

### 基本运行
```bash
python run.py
```

### 指定环境
```bash
python run.py --env prod
```

### 执行特定标记的用例
```bash
python run.py --mark smoke
```

### 指定单个YAML文件
```bash
python run.py --data login
```

### 生成HTML报告
```bash
python run.py --generate-report
```

## 查看报告

运行生成报告命令后，执行以下命令打开报告：
```bash
allure open reports/allure_html
```

## 日志查看

日志文件位于 `logs/` 目录下，按天生成，保留7天。

## 注意事项

1. 确保 `config/env.yaml` 中的环境配置正确
2. 编写YAML用例时，注意语法格式，特别是缩进
3. 对于数据库操作，确保数据库连接信息正确且具有相应权限
4. 首次运行时，会自动创建必要的目录结构
