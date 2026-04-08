"""兼容入口：统一从 testcases.security.payload.payload_config 导出 payload 常量与加载函数。"""

from testcases.security.payload.payload_config import SQL_INJECT_PAYLOADS, XSS_PAYLOADS, load_custom_payload

__all__ = ["SQL_INJECT_PAYLOADS", "XSS_PAYLOADS", "load_custom_payload"]

