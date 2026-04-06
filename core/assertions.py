# core/assertions.py
"""常用 HTTP / JSON / 性能断言，供用例复用。"""

import json
import logging
import time
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)


class ApiAssertions:
    """接口测试断言工具类（静态方法）。"""

    @staticmethod
    def assert_status_code(response: Any, expected: int) -> None:
        """断言 HTTP 状态码与期望值一致。

        参数:
            response: 含 status_code 的响应对象（如 requests.Response）。
            expected: 期望状态码。

        返回:
            无。

        异常:
            AssertionError: 状态码不一致时抛出。
        """
        actual = getattr(response, "status_code", None)
        logger.info("assert_status_code: expected=%s actual=%s", expected, actual)
        if actual != expected:
            logger.error("状态码不匹配，期望=%s，实际=%s", expected, actual)
            raise AssertionError(f"状态码不匹配，期望 {expected}，实际 {actual}")

    @staticmethod
    def assert_json_value(
        response_json: Dict[str, Any],
        key_path: str,
        expected_value: Any,
    ) -> None:
        """按点分路径断言 JSON 字段值（如 data.user.id）。

        参数:
            response_json: 解析后的 JSON 字典。
            key_path: 点分隔的键路径。
            expected_value: 期望的值。

        返回:
            无。

        异常:
            AssertionError: 键不存在或值不匹配时抛出。
        """
        actual: Any = response_json
        for part in key_path.split("."):
            if not isinstance(actual, dict) or part not in actual:
                logger.error("JSON 中缺少键路径：%s", key_path)
                raise AssertionError(f"JSON 中缺少键路径：{key_path}")
            actual = actual[part]

        logger.info(
            "assert_json_value: %s=%s expected=%s",
            key_path,
            actual,
            expected_value,
        )
        if actual != expected_value:
            logger.error(
                "JSON 值不匹配：路径=%s 期望=%s 实际=%s",
                key_path,
                expected_value,
                actual,
            )
            raise AssertionError(
                f"JSON 值不匹配：{key_path} 期望 {expected_value}，实际 {actual}"
            )

    @staticmethod
    def assert_response_time(
        response: Any,
        max_seconds: float,
        elapsed: Union[float, None] = None,
    ) -> None:
        """断言响应耗时不超过上限。

        若响应对象带有 elapsed 属性（requests.Response.elapsed），则优先使用；
        否则使用传入的 elapsed（秒）。

        参数:
            response: 响应对象；可为 None 当仅使用 elapsed 参数时。
            max_seconds: 允许的最大耗时（秒）。
            elapsed: 可选，手动传入耗时（秒）。

        返回:
            无。

        异常:
            AssertionError: 超时时抛出。
            ValueError: 无法取得耗时时抛出。
        """
        if elapsed is not None:
            used = float(elapsed)
        elif response is not None and hasattr(response, "elapsed"):
            used = response.elapsed.total_seconds()
        else:
            logger.error("assert_response_time: 无 elapsed 信息")
            raise ValueError("需要提供 elapsed 或带 elapsed 属性的 response")

        logger.info("assert_response_time: used=%.3fs max=%.3fs", used, max_seconds)
        if used > max_seconds:
            logger.error("响应超时：%.3fs > %.3fs", used, max_seconds)
            raise AssertionError(f"响应耗时 {used:.3f}s 超过上限 {max_seconds}s")


def assert_no_leak_keywords(text: str, forbidden: List[str]) -> None:
    """断言文本中（大小写不敏感）不包含给定敏感关键词。

    参数:
        text: 待检查的响应正文。
        forbidden: 禁止出现的关键词列表。

    返回:
        无。

    异常:
        AssertionError: 任一词命中时抛出。
    """
    lower = text.lower()
    for word in forbidden:
        if word.lower() in lower:
            logger.error("响应中包含敏感关键词：%s", word)
            raise AssertionError(f"响应中不应包含敏感关键词：{word}")


def safe_response_text(response: Any) -> str:
    """安全获取响应文本，非文本时回退为 JSON 字符串或 str()。

    参数:
        response: requests.Response 或类似对象。

    返回:
        字符串形式的响应体。

    异常:
        无。
    """
    try:
        return response.text
    except (AttributeError, UnicodeDecodeError, ValueError) as exc:
        logger.error("读取 response.text 失败：%s", exc)
        try:
            return json.dumps(response.json())
        except (AttributeError, TypeError, ValueError):
            return str(response)
