# testcases/security/payload/__init__.py
"""Payload 配置模块。"""

from .payload_config import SQL_INJECT_PAYLOADS, XSS_PAYLOADS, load_custom_payload

__all__ = ["SQL_INJECT_PAYLOADS", "XSS_PAYLOADS", "load_custom_payload"]
