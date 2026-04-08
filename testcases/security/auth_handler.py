"""认证处理模块：获取/缓存 Bearer Token，生成认证请求头。"""

import logging
import time
from typing import Any, Dict, Optional

from requests.exceptions import RequestException

from core.request_handler import RequestHandler

logger = logging.getLogger(__name__)


class AuthManager:
    """认证管理器：登录获取 token 并缓存，供安全检测模块复用。"""

    def __init__(
        self,
        request_handler: RequestHandler,
        login_path: str = "/login",
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """初始化认证管理器。

        参数:
            request_handler: 原项目 RequestHandler。
            login_path: 登录接口路径（相对 BASE_URL）。
            username: 用户名（可通过环境变量传入）。
            password: 密码。
        """
        self._request_handler = request_handler
        self._login_path = login_path
        self._username = username
        self._password = password

        self._cached_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    def clear_cache(self) -> None:
        """清除缓存 token。"""
        self._cached_token = None
        self._token_expires_at = 0.0

    def get_token(self, force_refresh: bool = False) -> Optional[str]:
        """获取 token（可缓存）。

        参数:
            force_refresh: 是否强制刷新 token。

        返回:
            token 字符串；未配置账号或获取失败返回 None。
        """
        if not force_refresh and self._cached_token and time.time() < self._token_expires_at:
            return self._cached_token
        if not self._username or not self._password:
            logger.info("未配置用户名/密码，跳过自动登录获取 token")
            return None

        body: Dict[str, Any] = {"username": self._username, "password": self._password}
        try:
            response = self._request_handler.post(self._login_path, json=body)
            response.raise_for_status()
            data = response.json()
        except RequestException as exc:
            logger.error("登录请求失败：%s", exc, exc_info=True)
            return None
        except ValueError as exc:
            logger.error("登录响应非 JSON：%s", exc, exc_info=True)
            return None
        except Exception as exc:
            logger.error("登录流程未预期异常：%s", exc, exc_info=True)
            return None

        # 兼容常见字段：token / access_token / data.token
        token = (
            data.get("token")
            or data.get("access_token")
            or (data.get("data") or {}).get("token")
        )
        if not token:
            logger.info("登录响应中未包含 token 字段")
            return None

        self._cached_token = str(token)
        ttl = float(data.get("expires_in", 3000))
        self._token_expires_at = time.time() + min(ttl, 3000)
        logger.info("已获取并缓存 token（日志已脱敏）")
        return self._cached_token

    def build_auth_headers(self) -> Dict[str, str]:
        """构建认证请求头（Bearer Token）。"""
        token = self.get_token()
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

