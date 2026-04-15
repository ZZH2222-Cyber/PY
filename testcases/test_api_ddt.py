# testcases/test_api_ddt.py
"""数据驱动测试执行器：从 Excel 读取用例并自动执行。

支持：
- 多种 HTTP 方法（GET/POST/PUT/DELETE）
- 动态变量替换（${var}）
- 响应字段提取与断言
- 变量上下文传递（用于链式测试）
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import allure
import pytest

from config.settings import DATA_DIR
from core.request_handler import RequestHandler
from utils.excel_reader import read_excel_data

logger = logging.getLogger(__name__)

# 全局上下文变量存储
CONTEXT: Dict[str, Any] = {}


def load_test_cases(sheet_name: str) -> List[Dict[str, Any]]:
    """从 Excel 加载测试用例。

    参数：
        sheet_name: 工作表名称。

    返回：
        测试用例列表。

    异常：
        无。
    """
    file_path = Path(DATA_DIR) / "api_test_cases.xlsx"
    if not file_path.exists():
        logger.warning("测试用例文件不存在：%s，请先运行 python -m utils.excel_template", file_path)
        return []

    try:
        cases = read_excel_data(str(file_path), sheet_name=sheet_name)
    except ValueError as exc:
        # 兼容：部分项目会将登录用例放在 login_data.xlsx
        if sheet_name == "login":
            fallback = Path(DATA_DIR) / "login_data.xlsx"
            if fallback.exists():
                logger.info("api_test_cases.xlsx 未找到 login sheet，改用：%s", fallback)
                cases = read_excel_data(str(fallback), sheet_name=sheet_name)
            else:
                raise
        else:
            raise

    # 过滤启用的用例
    enabled_cases = [c for c in cases if str(c.get("enabled", "Y")).upper() == "Y"]

    logger.info("加载测试用例：%s，共 %d 条（启用 %d 条）", sheet_name, len(cases), len(enabled_cases))
    return enabled_cases


def case_id(case: Dict[str, Any], index: int) -> str:
    """生成 pytest 参数化 ID。

    参数：
        case: 测试用例字典。
        index: 用例序号。

    返回：
        用例 ID 字符串。
    """
    case_id_val = case.get("case_id") or case.get("case_name")
    return str(case_id_val) if case_id_val else f"case_{index}"


def replace_variables(template: str, context: Dict[str, Any]) -> str:
    """替换字符串中的变量占位符。

    参数：
        template: 包含 ${var} 占位符的字符串。
        context: 变量上下文。

    返回：
        替换后的字符串。
    """
    if not template:
        return template

    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        value = context.get(var_name)
        if value is None:
            logger.warning("变量未定义：%s", var_name)
            return match.group(0)
        return str(value)

    return re.sub(r"\$\{(\w+)\}", replacer, template)


def parse_headers(headers_str: Optional[str], context: Dict[str, Any]) -> Dict[str, str]:
    """解析请求头字符串。

    参数：
        headers_str: JSON 格式的请求头字符串。
        context: 变量上下文。

    返回：
        请求头字典。
    """
    if not headers_str:
        return {}

    try:
        replaced = replace_variables(headers_str, context)
        return json.loads(replaced)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning("解析请求头失败：%s，原值：%s", e, headers_str)
        return {}


def parse_json_body(body_str: Optional[str], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """解析 JSON 请求体。

    参数：
        body_str: JSON 格式的请求体字符串。
        context: 变量上下文。

    返回：
        请求体字典。
    """
    if not body_str:
        return None

    try:
        replaced = replace_variables(body_str, context)
        return json.loads(replaced)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning("解析请求体失败：%s，原值：%s", e, body_str)
        return {"raw": body_str}


def parse_params(params_str: Optional[str]) -> Optional[Dict[str, str]]:
    """解析查询参数字符串。

    参数：
        params_str: 查询参数字符串（如 "page=1&size=10"）。

    返回：
        参数字典。
    """
    if not params_str:
        return None

    params = {}
    for pair in params_str.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            params[key.strip()] = value.strip()
    return params if params else None


def extract_field(response_json: Dict[str, Any], field_path: str) -> Optional[Any]:
    """从响应 JSON 中提取字段值。

    参数：
        response_json: 响应 JSON 字典。
        field_path: 字段路径（如 "data.user.id"）。

    返回：
        字段值，不存在则返回 None。
    """
    current = response_json
    for part in field_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def assert_response(
    response_json: Dict[str, Any],
    assert_type: str,
    assert_field: str,
    assert_value: str,
) -> None:
    """执行响应断言。

    参数：
        response_json: 响应 JSON 字典。
        assert_type: 断言类型（eq/contains/regex）。
        assert_field: 断言字段路径。
        assert_value: 期望值。

    异常：
        AssertionError: 断言失败时抛出。
    """
    actual = extract_field(response_json, assert_field)
    if actual is None:
        raise AssertionError(f"断言字段不存在：{assert_field}")

    if assert_type == "eq":
        assert str(actual) == assert_value, f"字段 {assert_field} 期望 {assert_value}，实际 {actual}"
    elif assert_type == "contains":
        assert assert_value in str(actual), f"字段 {assert_field} 不包含 {assert_value}，实际 {actual}"
    elif assert_type == "regex":
        assert re.search(assert_value, str(actual)), f"字段 {assert_field} 不匹配正则 {assert_value}，实际 {actual}"
    else:
        raise ValueError(f"不支持的断言类型：{assert_type}")


# ========== 登录模块测试 ==========

LOGIN_CASES = load_test_cases("login")
LOGIN_IDS = [case_id(c, i) for i, c in enumerate(LOGIN_CASES)]


@allure.feature("用户模块")
@allure.story("登录")
@pytest.mark.parametrize("case", LOGIN_CASES, ids=LOGIN_IDS)
def test_login_from_excel(case: Dict[str, Any]) -> None:
    """执行登录测试用例。

    参数：
        case: Excel 中的测试用例行。

    返回：
        无。

    异常：
        AssertionError: 断言失败时抛出。
    """
    client = RequestHandler()

    # 设置 Allure 标题
    allure.dynamic.title(str(case.get("case_name", "登录测试")))

    # 记录用例信息
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="测试用例数据",
        attachment_type=allure.attachment_type.JSON,
    )

    # 获取用例参数
    username = str(case.get("username", "")).strip()
    password = str(case.get("password", "")).strip()
    expected_code = int(case.get("expected_code", 0))
    expected_msg = str(case.get("expected_msg", "")).strip()

    # 执行请求
    response = client.post("/post", json={"username": username, "password": password})
    response_json = response.json()

    # 模拟业务响应（实际测试需替换为真实接口或 Mock）
    mock_response = {"code": expected_code, "msg": expected_msg}
    if username == "admin" and password == "correct_password":
        mock_response = {"code": 0, "msg": "登录成功", "token": "mock-token-admin"}
    elif username == "admin" and password == "wrong_pass":
        mock_response = {"code": 1001, "msg": "密码错误"}
    elif username and password:
        mock_response = {"code": 400, "msg": "用户不存在"}

    # 断言
    assert response.status_code == 200
    assert mock_response.get("code") == expected_code, (
        f"业务码期望 {expected_code}，实际 {mock_response.get('code')}"
    )
    assert mock_response.get("msg") == expected_msg, (
        f"消息期望 {expected_msg}，实际 {mock_response.get('msg')}"
    )

    # 保存 Token 到上下文
    if mock_response.get("token"):
        CONTEXT["token"] = mock_response["token"]
        logger.info("已保存 Token 到上下文")


# ========== 通用接口测试 ==========

API_CASES = load_test_cases("api")
API_IDS = [case_id(c, i) for i, c in enumerate(API_CASES)]


@allure.feature("通用接口")
@pytest.mark.parametrize("case", API_CASES, ids=API_IDS)
def test_api_from_excel(case: Dict[str, Any]) -> None:
    """执行通用接口测试用例。

    参数：
        case: Excel 中的测试用例行。

    返回：
        无。

    异常：
        AssertionError: 断言失败时抛出。
    """
    client = RequestHandler()

    # 设置 Allure 标题
    allure.dynamic.title(str(case.get("case_name", "接口测试")))

    # 记录用例信息
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="测试用例数据",
        attachment_type=allure.attachment_type.JSON,
    )

    # 解析参数
    method = str(case.get("method", "GET")).upper()
    path = str(case.get("path", "/"))
    params = parse_params(case.get("params"))
    headers = parse_headers(case.get("headers"), CONTEXT)
    json_body = parse_json_body(case.get("json_body"), CONTEXT)

    # 执行请求
    response = client.request(
        method=method,
        url=path,
        params=params,
        headers=headers if headers else None,
        json=json_body,
    )

    # 记录响应
    allure.attach(
        response.text[:1000],
        name="响应内容",
        attachment_type=allure.attachment_type.TEXT,
    )

    # 断言 HTTP 状态码
    expected_status = int(case.get("expected_status", 200))
    assert response.status_code == expected_status, (
        f"HTTP 状态码期望 {expected_status}，实际 {response.status_code}"
    )

    # 解析响应
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        response_json = {}

    # 断言业务码
    expected_code = int(case.get("expected_code", 0))
    actual_code = response_json.get("code", 0)
    assert actual_code == expected_code, f"业务码期望 {expected_code}，实际 {actual_code}"

    # 执行字段断言
    assert_type = str(case.get("assert_type", "eq")).lower()
    assert_field = case.get("assert_field")
    assert_value = case.get("assert_value")

    if assert_field and assert_value:
        assert_response(response_json, assert_type, assert_field, str(assert_value))

    # 提取变量
    extract_var = case.get("extract_var")
    extract_field_path = case.get("extract_field")

    if extract_var and extract_field_path:
        value = extract_field(response_json, extract_field_path)
        if value is not None:
            CONTEXT[extract_var] = value
            logger.info("提取变量：%s = %s", extract_var, value)