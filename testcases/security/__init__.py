"""安全测试子包：安全 payload 与自动化检测入口。"""

from testcases.security.bug_logger import BugLogGenerator
from testcases.security.detector_core import SecurityDetector
from testcases.security.interface_config import TARGET_INTERFACES, get_all_interfaces, get_interface_config
from testcases.security.payload_config import SQL_INJECT_PAYLOADS, XSS_PAYLOADS, load_custom_payload

__all__ = [
    "BugLogGenerator",
    "SecurityDetector",
    "TARGET_INTERFACES",
    "get_interface_config",
    "get_all_interfaces",
    "SQL_INJECT_PAYLOADS",
    "XSS_PAYLOADS",
    "load_custom_payload",
]
