# api/user_api.py
"""用户相关接口：登录、查询用户；内部缓存 Token 并自动携带。"""

import logging
from typing import Any, Dict, Optional

from core.request_handler import RequestHandler

logger = logging.getLogger(__name__)


class UserAPI:
    """封装 /login 与 /user/{id}；登录成功后缓存 Token 供后续请求使用。"""

    def __init__(self, client: Optional[RequestHandler] = None) -> None:
        """初始化 API 客户端。

        参数:
            client: 自定义 RequestHandler；默认新建实例。

        返回:
            无。

        异常:
            无。
        """
        self.client = client or RequestHandler()
        self._token: Optional[str] = None
        self._cached_username: Optional[str] = None
        self._cached_password: Optional[str] = None

    def clear_token(self) -> None:
        """清空本地 Token 与缓存的登录凭据。

        参数:
            无。

        返回:
            无。

        异常:
            无。
        """
        self._token = None
        self._cached_username = None
        self._cached_password = None
        logger.info("已清空 Token 缓存")

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """调用 POST /login，成功则从响应中提取 token 并缓存。

        期望业务响应体包含可选字段：token 或 data.token（按项目调整）。

        参数:
            username: 用户名。
            password: 密码。

        返回:
            解析后的 JSON 字典。

        异常:
            requests.RequestException: 底层 HTTP 请求失败（由 RequestHandler 记录后抛出）。
            ValueError: 响应非合法 JSON。
        """
        payload = {"username": username, "password": password}
        logger.info("调用登录接口：username=%s", username)

        response = self.client.post("/login", json=payload)
        try:
            data = response.json()
        except ValueError as exc:
            logger.error("登录响应非 JSON：%s", exc)
            raise

        # 常见字段名兼容
        token = (
            data.get("token")
            or data.get("access_token")
            or (data.get("data") or {}).get("token")
        )
        if token:
            self._token = str(token)
            self._cached_username = username
            self._cached_password = password
            logger.info("登录成功，已缓存 Token")
        else:
            logger.info("登录响应中未包含 token 字段（可能为失败用例）")

        return data

    def _ensure_token(self) -> str:
        """若尚无 Token，则使用最近一次成功的用户名密码再次登录。

        参数:
            无。

        返回:
            当前有效的 Token 字符串。

        异常:
            RuntimeError: 无法自动登录取得 Token。
            requests.RequestException: 网络错误。
        """
        if self._token:
            return self._token
        if self._cached_username and self._cached_password:
            logger.info("Token 缺失，尝试使用缓存凭据重新登录")
            self.login(self._cached_username, self._cached_password)
        if not self._token:
            logger.error("无法获取 Token，请先调用 login 成功")
            raise RuntimeError("缺少 Token，请先执行登录且响应包含 token")
        return self._token

    def get_user(
        self,
        user_id: int,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """GET /user/{id}，默认 Authorization: Bearer <token>。

        未传 token 时使用 _ensure_token() 自动补全。

        参数:
            user_id: 用户 ID。
            token: 可选；显式传入则优先使用，不读缓存。

        返回:
            解析后的 JSON 字典。

        异常:
            requests.RequestException: 网络错误。
            ValueError: 响应非合法 JSON。
        """
        auth_token = token if token is not None else self._ensure_token()
        headers = {"Authorization": f"Bearer {auth_token}"}
        logger.info("调用获取用户接口：user_id=%s", user_id)

        response = self.client.get(f"/user/{user_id}", headers=headers)
        try:
            return response.json()
        except ValueError as exc:
            logger.error("获取用户响应非 JSON：%s", exc)
            raise

    def create_user(self, name: str, email: str, token: Optional[str] = None) -> Dict[str, Any]:
        """POST /user，创建用户；未传 token 时使用缓存。

        参数:
            name: 用户名。
            email: 邮箱。
            token: 可选鉴权令牌。

        返回:
            JSON 字典。

        异常:
            ValueError: 响应非 JSON。
        """
        auth_token = token if token is not None else self._ensure_token()
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"name": name, "email": email}
        logger.info("调用创建用户：name=%s email=%s", name, email)
        response = self.client.post("/user", json=payload, headers=headers)
        try:
            return response.json()
        except ValueError as exc:
            logger.error("创建用户响应非 JSON：%s", exc)
            raise

    def update_user(
        self,
        user_id: int,
        data: Dict[str, Any],
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """PUT /user/{id}；未传 token 时使用缓存。

        参数:
            user_id: 用户 ID。
            data: 更新字段。
            token: 可选鉴权令牌。

        返回:
            JSON 字典。

        异常:
            ValueError: 响应非 JSON。
        """
        auth_token = token if token is not None else self._ensure_token()
        headers = {"Authorization": f"Bearer {auth_token}"}
        logger.info("调用更新用户：user_id=%s", user_id)
        response = self.client.put(f"/user/{user_id}", json=data, headers=headers)
        try:
            return response.json()
        except ValueError as exc:
            logger.error("更新用户响应非 JSON：%s", exc)
            raise

    def delete_user(self, user_id: int, token: Optional[str] = None) -> Dict[str, Any]:
        """DELETE /user/{id}；未传 token 时使用缓存。

        参数:
            user_id: 用户 ID。
            token: 可选鉴权令牌。

        返回:
            JSON 字典。

        异常:
            ValueError: 响应非 JSON。
        """
        auth_token = token if token is not None else self._ensure_token()
        headers = {"Authorization": f"Bearer {auth_token}"}
        logger.info("调用删除用户：user_id=%s", user_id)
        response = self.client.delete(f"/user/{user_id}", headers=headers)
        try:
            return response.json()
        except ValueError as exc:
            logger.error("删除用户响应非 JSON：%s", exc)
            raise
