# core/request_handler.py
"""封装 requests：统一 URL、超时、日志与异常处理。"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests
from requests import Response
from requests.exceptions import RequestException

from config.settings import BASE_URL, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

SENSITIVE_KEYS: List[str] = [
    "password",
    "pwd",
    "token",
    "secret",
    "apikey",
    "api_key",
    "authorization",
]


class RequestHandler:
    """HTTP 会话封装：在单例 Session 上发送 get/post/put/delete。"""

    def __init__(self, base_url: str = BASE_URL) -> None:
        """创建会话并记录基础地址。

        参数:
            base_url: 接口根地址，默认读取配置。

        返回:
            无。

        异常:
            无。
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    @staticmethod
    def _mask_sensitive(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """对字典中的敏感字段打码，便于打日志。

        参数:
            data: 请求体或查询参数等。

        返回:
            脱敏后的副本；data 为 None 时返回 None。

        异常:
            无。
        """
        if data is None:
            return None
        masked = dict(data)
        for key in masked:
            if key.lower() in SENSITIVE_KEYS:
                masked[key] = "******"
        return masked

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        """统一请求入口：拼 URL、默认超时、记录日志、抛出网络异常。

        参数:
            method: http 方法名，如 get、post。
            url: 相对路径，以 / 开头。
            kwargs: 透传给 requests.Session.request。

        返回:
            requests.Response。

        异常:
            requests.RequestException: 网络层错误，记录日志后原样抛出。
        """
        path = url if url.startswith("/") else f"/{url}"
        full_url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)

        logger.info("Request: %s %s", method.upper(), full_url)
        logger.debug("Request params: %s", kwargs.get("params"))
        logger.debug("Request json: %s", self._mask_sensitive(kwargs.get("json")))
        logger.debug("Request data: %s", self._mask_sensitive(kwargs.get("data")))

        start = time.perf_counter()
        try:
            response = self.session.request(method, full_url, **kwargs)
            cost = time.perf_counter() - start
            logger.info(
                "Response status: %s elapsed=%.3fs",
                response.status_code,
                cost,
            )
            logger.debug("Response body (truncated): %s", response.text[:500])
            return response
        except RequestException as exc:
            logger.error("Request failed: %s", exc, exc_info=True)
            raise

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Response:
        """发送 GET 请求。

        参数:
            url: 相对路径。
            params: 查询参数。
            kwargs: 其他 requests 参数。

        返回:
            requests.Response。

        异常:
            requests.RequestException: 请求失败时抛出。
        """
        return self.request("get", url, params=params, **kwargs)

    def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Response:
        """发送 POST 请求。

        参数:
            url: 相对路径。
            json: JSON 体。
            data: 表单体。
            kwargs: 其他 requests 参数。

        返回:
            requests.Response。

        异常:
            requests.RequestException: 请求失败时抛出。
        """
        return self.request("post", url, json=json, data=data, **kwargs)

    def put(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Response:
        """发送 PUT 请求。

        参数:
            url: 相对路径。
            json: JSON 体。
            data: 表单体。
            kwargs: 其他 requests 参数。

        返回:
            requests.Response。

        异常:
            requests.RequestException: 请求失败时抛出。
        """
        return self.request("put", url, json=json, data=data, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        """发送 DELETE 请求。

        参数:
            url: 相对路径。
            kwargs: 其他 requests 参数。

        返回:
            requests.Response。

        异常:
            requests.RequestException: 请求失败时抛出。
        """
        return self.request("delete", url, **kwargs)
