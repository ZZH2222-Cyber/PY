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
│   └── ai_helper.py         # DeepSeek 生成用例 / 模拟数据
├── testcases/
│   ├── conftest.py
│   ├── test_login.py
│   ├── test_security.py
│   └── security/payload/    # 安全 payload 配置
├── data/                    # 测试数据（含 login_data.xlsx）
├── reports/                 # Allure 结果（pytest 默认写入 allure_results）
├── logs/test.log
├── docs/AI_usage_log.md
├── .github/workflows/ci.yml
├── requirements.txt
└── pytest.ini
```

## 快速开始

```bash
cd api-auto-test-framework
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest
```

查看 Allure 报告（需本机安装 [Allure](https://docs.qameta.io/allure/)）：

```bash
allure serve reports/allure_results
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `BASE_URL` | 被测 API 根地址，默认 `https://httpbin.org` |
| `REQUEST_TIMEOUT` | 超时秒数，默认 `10` |
| `LOG_LEVEL` | 日志级别，默认 `INFO` |
| `DEEPSEEK_API_KEY` | 若设置则 `utils/ai_helper.py` 走真实 DeepSeek，否则返回内置模拟用例 |
| `SECURITY_SQL_SAMPLES` / `SECURITY_XSS_SAMPLES` | 安全用例抽样数量，默认各 `15`；设大数字可接近全量 |

## 代码规范摘要

文件名小写+下划线；类大驼峰；函数与变量小写+下划线；常量全大写；函数/类需文档字符串（功能、参数、返回、异常）；`logging` 记录关键步骤；具体异常类型；类型注解；导入顺序：标准库 → 第三方 → 本地。

## AI 使用记录

见 [docs/AI_usage_log.md](docs/AI_usage_log.md)。
