# 基于 Python 的 AI 增强型接口自动化测试平台

技术栈：`requests`、`pytest`、`allure-pytest`、`openpyxl`、可选 `pymysql`、可选 DeepSeek API、`GitHub Actions`。

## 目录结构

```
api-auto-test-framework/
├── config/settings.py       # 全局配置、日志
├── core/
│   ├── request_handler.py   # HTTP 封装
│   └── assertions.py        # 断言工具
├── api/user_api.py          # 用户接口（登录 + Token 缓存）
├── utils/
│   ├── excel_reader.py      # Excel 数据驱动
│   ├── excel_template.py    # Excel 测试用例模板生成
│   └── ai_helper.py         # DeepSeek 生成用例 / 模拟数据
├── testcases/
│   ├── conftest.py
│   ├── test_login.py        # 登录测试（数据驱动）
│   ├── test_api_ddt.py      # 通用接口测试（数据驱动）
│   ├── test_security.py
│   └── security/payload/    # 安全 payload 配置
├── data/                    # 测试数据（含 Excel 测试用例）
│   ├── login_data.xlsx
│   └── api_test_cases.xlsx  # 规范化测试用例模板
├── reports/                 # Allure 结果
├── logs/test.log
├── runtest.py               # 测试执行入口脚本
├── docs/AI_usage_log.md
├── .github/workflows/ci.yml
├── requirements.txt
└── pytest.ini
```

## 快速开始

### 1. 安装依赖

```bash
cd api-auto-test-framework
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 生成 Excel 测试用例模板

```bash
python -m utils.excel_template
```

将在 `data/` 目录下生成 `api_test_cases.xlsx` 文件。

### 3. 运行测试

```bash
# 方式一：使用 runtest.py（推荐）
python runtest.py                      # 运行所有测试
python runtest.py -t test_login        # 运行指定测试文件
python runtest.py -m login             # 运行带 login 标记的测试
python runtest.py --allure             # 运行测试并生成 Allure 报告数据
python runtest.py --allure --open      # 生成并打开 Allure 报告
python runtest.py --report             # 仅生成 Allure HTML 报告

# 方式二：直接使用 pytest
pytest                                 # 运行所有测试
pytest testcases/test_login.py -v      # 运行指定文件
pytest -m login                        # 按标记运行
```

### 4. 查看 Allure 报告

```bash
# 方式一：启动本地服务（推荐）
allure serve reports/allure_results

# 方式二：生成静态 HTML 报告
allure generate reports/allure_results -o reports/allure_report --clean
```

## Excel 测试用例规范

### 用例文件结构

生成的 `api_test_cases.xlsx` 包含以下工作表：

| 工作表 | 说明 |
|--------|------|
| `login` | 登录接口测试用例 |
| `user` | 用户管理接口测试用例 |
| `api` | 通用接口测试用例 |
| `字段说明` | 各字段的详细说明 |

### 核心字段说明

| 字段名 | 必填 | 说明 | 示例 |
|--------|------|------|------|
| `case_id` | 是 | 用例唯一标识 | TC001 |
| `case_name` | 是 | 用例名称 | 正常登录-管理员 |
| `priority` | 是 | 优先级：高/中/低 | 高 |
| `module` | 是 | 所属模块 | 用户模块 |
| `method` | 是 | HTTP方法 | POST |
| `path` | 是 | 接口路径 | /login |
| `params` | 否 | 查询参数 | page=1&size=10 |
| `headers` | 否 | 请求头（JSON） | {"Authorization": "Bearer ${token}"} |
| `json_body` | 否 | JSON请求体 | {"name": "test"} |
| `expected_status` | 是 | HTTP状态码 | 200 |
| `expected_code` | 是 | 业务状态码 | 0 |
| `assert_field` | 否 | 断言字段 | data.id |
| `assert_value` | 否 | 期望值 | 1 |
| `enabled` | 是 | 是否启用 | Y/N |

### 变量替换

支持在 `headers` 和 `json_body` 中使用 `${var}` 占位符：

```json
{"Authorization": "Bearer ${token}"}
```

变量值会在测试执行过程中自动提取和替换。

## 环境变量

| 变量 | 说明 |
|------|------|
| `BASE_URL` | 被测 API 根地址，默认 `https://httpbin.org` |
| `REQUEST_TIMEOUT` | 超时秒数，默认 `10` |
| `API_KEY` | （可选）API 密钥；设置后会在所有请求里自动携带 |
| `API_KEY_HEADER` | （可选）API 密钥对应的请求头名，默认 `X-API-Key`（也可设为 `Authorization`） |
| `API_KEY_PREFIX` | （可选）API Key 前缀，默认空；常见可设为 `Bearer`（最终为 `Bearer <API_KEY>`） |
| `LOG_LEVEL` | 日志级别，默认 `INFO` |
| `DEEPSEEK_API_KEY` | 若设置则 `utils/ai_helper.py` 走真实 DeepSeek，否则返回内置模拟用例 |
| `SECURITY_SQL_SAMPLES` / `SECURITY_XSS_SAMPLES` | 安全用例抽样数量，默认各 `15` |

### 团队共享配置（推荐）

项目支持从根目录的 `.env` 自动读取环境变量（使用 `python-dotenv`），便于队友拉取代码后直接运行。

- 将仓库里的 `.env.example` 复制为 `.env`
- 在 `.env` 里填入你自己的 `BASE_URL`、`API_KEY` 等
- `.env` 已在 `.gitignore` 中忽略，不会被提交到仓库

## runtest.py 命令行参数

```
usage: runtest.py [-h] [-t TEST_PATH] [-m MARKERS] [--allure] [--open] [--report] [--init] [extra ...]

接口自动化测试框架 - 执行入口

optional arguments:
  -t, --test TEST_PATH   指定测试文件或目录路径
  -m, --marker MARKERS   pytest 标记过滤（如 login, security）
  --allure               生成 Allure 报告数据
  --open                 打开 Allure 报告（需配合 --allure 使用）
  --report               仅生成 Allure HTML 报告（不运行测试）
  --init                 初始化项目目录结构
  extra                  额外的 pytest 参数（如 -k 'test_login'）

示例：
  python runtest.py                      # 运行所有测试
  python runtest.py -t test_login        # 运行指定测试文件
  python runtest.py -m login             # 运行带 login 标记的测试
  python runtest.py --allure             # 运行测试并生成 Allure 报告
  python runtest.py --allure --open      # 生成并打开 Allure 报告
  python runtest.py --report             # 仅生成 Allure HTML 报告
```

## 代码规范摘要

文件名小写+下划线；类大驼峰；函数与变量小写+下划线；常量全大写；函数/类需文档字符串（功能、参数、返回、异常）；`logging` 记录关键步骤；具体异常类型；类型注解；导入顺序：标准库 → 第三方 → 本地。

## AI 使用记录

见 [docs/AI_usage_log.md](docs/AI_usage_log.md)。