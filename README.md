# 基于Python的AI增强型接口自动化测试平台

## 项目简介

这是一个Python接口自动化测试框架，能够对任意Web API进行自动化测试，并生成美观的测试报告。在此基础上，增加了AI辅助测试用例生成和AI安全测试两个亮点功能。

## 项目结构

```
├── src/              # 源代码目录
│   ├── core/         # 核心引擎
│   ├── utils/        # 工具函数
│   │   ├── excel_utils.py  # Excel读取工具
│   │   └── db_utils.py     # 数据库查询工具
│   └── tests/        # 测试用例
├── data/             # 测试数据
│   └── test_data.xlsx # 测试Excel数据文件
├── docs/             # 文档
├── requirements.txt  # 依赖包
├── test_utils.py     # 工具测试脚本
└── create_test_excel.py # 测试Excel文件生成脚本
```

## 核心功能

1. **核心引擎**：封装Requests，统一处理请求、响应、异常、日志
2. **测试管理**：组织测试用例，支持数据驱动
3. **断言库**：状态码、JSON字段、响应时间断言
4. **报告系统**：生成HTML测试报告
5. **数据库校验**：验证接口对数据库的影响
6. **AI用例生成**：调用大模型API，根据接口描述自动生成测试数据
7. **AI安全检测**：识别接口中的提示词注入、SQL注入风险
8. **CI/CD**：自动化运行测试，展示持续集成能力

## 技术栈

- Python 3.9+
- requests - HTTP请求库
- pytest - 测试框架
- openpyxl - Excel操作
- pyyaml - YAML配置文件处理
- pymysql - 数据库连接
- allure-pytest - 测试报告生成
- jsonschema - JSON Schema验证

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 准备测试数据

创建Excel测试数据文件：

```bash
python create_test_excel.py
```

### 2. 测试Excel读取功能

```bash
python test_utils.py
```

### 3. 编写测试用例

在`src/tests`目录下创建测试用例文件，使用pytest框架编写测试。

### 4. 运行测试

```bash
pytest
```

### 5. 生成测试报告

```bash
pytest --alluredir=./allure-results
allure serve ./allure-results
```

## 工具函数使用示例

### Excel读取工具

```python
from utils.excel_utils import read_excel

# 读取Excel文件
data = read_excel('data/test_data.xlsx')
print(data)

# 读取指定工作表
data = read_excel('data/test_data.xlsx', sheet_name='Sheet1')
print(data)
```

### 数据库查询工具

```python
from utils.db_utils import connect_db, query_db, close_db

# 连接数据库
conn = connect_db(host='localhost', port=3306, user='root', password='your_password', db='test')

# 执行查询
sql = "SELECT * FROM users WHERE id = %s"
result = query_db(conn, sql, (1,))
print(result)

# 关闭连接
close_db(conn)
```

## 团队成员

- **网安专业队友**：负责核心引擎与AI特色功能
- **计科专业队友**：负责工具开发与文档

## 项目目标

冲击广东省大学生计算机设计大赛省赛二等奖以上，打造一份高含金量的简历项目。
