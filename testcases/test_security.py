# testcases/test_security.py
"""安全向检测：将恶意 payload 作为查询参数提交，检查响应是否泄露典型错误信息。"""

import os
from typing import Any, List, Tuple

import allure
import pytest

from config.settings import BASE_URL
from core.assertions import assert_no_leak_keywords, safe_response_text
from core.request_handler import RequestHandler
from testcases.security.payload.payload_config import (
    SQL_INJECT_PAYLOADS,
    XSS_PAYLOADS,
)

# 默认抽样条数，避免对 httpbin 频繁请求拖慢 CI；全量可设环境变量为较大数字
_SQL_N = int(os.environ.get("SECURITY_SQL_SAMPLES", "15"))
_XSS_N = int(os.environ.get("SECURITY_XSS_SAMPLES", "15"))

# 若响应正文出现下列片段，视为可能存在信息泄露（可按被测系统调整）
_FORBIDDEN_SNIPPETS: Tuple[str, ...] = (
    "sql syntax",
    "syntax error",
    "mysql",
    "sqlite",
    "ora-",
    "postgresql",
    "sql server",
    "odbc",
    "stack trace",
    "internal server error",
)


def _payload_matrix() -> List[Tuple[str, str]]:
    """组装 (类型, payload) 列表供参数化。

    参数:
        无。

    返回:
        列表，元素为 (类别名, payload 字符串)。

    异常:
        无。
    """
    sql_list = SQL_INJECT_PAYLOADS[:_SQL_N]
    xss_list = XSS_PAYLOADS[:_XSS_N]
    rows: List[Tuple[str, str]] = [("sql", p) for p in sql_list]
    rows.extend(("xss", p) for p in xss_list)
    return rows


_MATRIX = _payload_matrix()
_IDS = [f"{kind}_{idx}" for idx, (kind, _) in enumerate(_MATRIX)]


@allure.feature("安全测试")
@allure.story("注入与 XSS 探测")
class TestSecurity:
    """对探测接口发送 payload，断言响应不含典型数据库/栈错误片段。"""

    @pytest.mark.parametrize("kind,payload", _MATRIX, ids=_IDS)
    def test_payload_not_trigger_server_error_leak(
        self,
        kind: str,
        payload: str,
    ) -> None:
        """演示：请求 httpbin /get 并检查响应正文。

        对接真实业务时，请将 client.get 的 path/参数改为实际接口，并结合鉴权与风控策略
        调整断言（例如仅允许固定错误码、禁止堆栈回显等）。

        参数:
            kind: sql 或 xss。
            payload: 具体攻击串。

        返回:
            无。

        异常:
            AssertionError: 命中禁止片段时抛出。
            requests.RequestException: 网络错误。
        """
        allure.dynamic.title(f"{kind.upper()} — {payload[:80]}")

        client = RequestHandler(base_url=BASE_URL)
        response = client.get("/get", params={"q": payload})

        assert response.status_code == 200, f"期望 200，实际 {response.status_code}"
        text = safe_response_text(response)
        assert_no_leak_keywords(text, list(_FORBIDDEN_SNIPPETS))
