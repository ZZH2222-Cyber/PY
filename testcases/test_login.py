# testcases/test_login.py
"""登录接口数据驱动测试：Excel + pytest + Allure；HTTP 由 responses 桩替换。"""

import json
import os
from typing import Any, Dict, List, Tuple

import allure
import pytest
import responses

from api.user_api import UserAPI
from config.settings import BASE_URL, DATA_DIR
from utils.excel_reader import read_excel_data


def _load_login_matrix() -> List[Dict[str, Any]]:
    """读取登录测试数据表。

    参数:
        无。

    返回:
        每行一个字典。

    异常:
        与 read_excel_data 相同。
    """
    path = os.path.join(DATA_DIR, "login_data.xlsx")
    return read_excel_data(path, sheet_name="login")


def _row_id(row: Dict[str, Any], index: int) -> str:
    """为 parametrize 生成可读 id。

    参数:
        row: Excel 行字典。
        index: 行序号。

    返回:
        用例标识字符串。

    异常:
        无。
    """
    name = row.get("case_name")
    if name is not None and str(name).strip():
        return str(name).strip()
    return f"row_{index}"


def _coerce_expected_code(raw: Any) -> int:
    """Excel 数字常读成 float，统一转为 int。

    参数:
        raw: 单元格原值。

    返回:
        整型业务码。

    异常:
        ValueError: 无法转换时抛出。
    """
    if raw is None:
        raise ValueError("expected_code 为空")
    if isinstance(raw, float):
        return int(raw)
    if isinstance(raw, int):
        return raw
    return int(str(raw).strip())


_MATRIX = _load_login_matrix()
_IDS = [_row_id(r, i) for i, r in enumerate(_MATRIX)]


def _login_stub(request: Any) -> Tuple[int, Dict[str, str], str]:
    """模拟业务登录：按用户名密码返回 code、msg、token。

    参数:
        request: responses 传入的请求对象。

    返回:
        (status_code, headers, body) 三元组。

    异常:
        无。
    """
    raw_body = request.body
    if isinstance(raw_body, bytes):
        raw_body = raw_body.decode("utf-8", errors="replace")
    try:
        payload = json.loads(raw_body) if raw_body else {}
    except (TypeError, ValueError):
        payload = {}

    username = payload.get("username")
    password = payload.get("password")

    if username == "admin" and password == "correct_password":
        body = {"code": 0, "msg": "登录成功", "token": "mock-token-admin"}
    elif username == "admin" and password == "wrong_pass":
        body = {"code": 1001, "msg": "密码错误"}
    else:
        body = {"code": 400, "msg": "用户不存在"}

    return (200, {}, json.dumps(body, ensure_ascii=False))


@allure.feature("用户模块")
@allure.story("登录")
class TestLogin:
    """登录场景：数据来自 data/login_data.xlsx。"""

    @responses.activate
    @pytest.mark.parametrize("row", _MATRIX, ids=_IDS)
    def test_login_from_excel(self, row: Dict[str, Any]) -> None:
        """根据 Excel 行调用 UserAPI.login 并校验 code、msg。

        参数:
            row: 单行测试数据。

        返回:
            无。

        异常:
            AssertionError: 断言失败时抛出。
        """
        url = f"{BASE_URL.rstrip('/')}/login"
        responses.add_callback(
            responses.POST,
            url,
            callback=_login_stub,
            content_type="application/json",
        )

        username = str(row.get("username", "")).strip()
        password = str(row.get("password", "")).strip()
        exp_code = _coerce_expected_code(row.get("expected_code"))
        exp_msg = str(row.get("expected_msg", "")).strip()

        title = row.get("case_name") or "登录用例"
        allure.dynamic.title(str(title))

        api = UserAPI()
        result = api.login(username, password)

        assert result.get("code") == exp_code, (
            f"code 期望 {exp_code} 实际 {result.get('code')}"
        )
        assert result.get("msg") == exp_msg, (
            f"msg 期望 {exp_msg!r} 实际 {result.get('msg')!r}"
        )

    @responses.activate
    def test_get_user_after_login_uses_cached_token(self) -> None:
        """登录成功后不传入 token 调用 get_user，应自动携带缓存的 Bearer。

        参数:
            无。

        返回:
            无。

        异常:
            AssertionError: 断言失败时抛出。
        """
        base = BASE_URL.rstrip("/")

        def login_cb(request: Any) -> Tuple[int, Dict[str, str], str]:
            return (
                200,
                {},
                json.dumps(
                    {"code": 0, "msg": "ok", "token": "cached-token-xyz"},
                    ensure_ascii=False,
                ),
            )

        user_body = {"id": 1, "name": "演示用户"}

        def user_cb(request: Any) -> Tuple[int, Dict[str, str], str]:
            auth = request.headers.get("Authorization", "")
            assert auth == "Bearer cached-token-xyz", f"Authorization 异常: {auth!r}"
            return (200, {}, json.dumps(user_body, ensure_ascii=False))

        responses.add_callback(
            responses.POST,
            f"{base}/login",
            callback=login_cb,
            content_type="application/json",
        )
        responses.add_callback(
            responses.GET,
            f"{base}/user/1",
            callback=user_cb,
            content_type="application/json",
        )

        allure.dynamic.title("获取用户 — 使用缓存 Token")

        api = UserAPI()
        api.login("admin", "correct_password")
        data = api.get_user(1)
        assert data == user_body
