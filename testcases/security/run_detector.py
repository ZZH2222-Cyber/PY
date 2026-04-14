"""安全检测主执行模块：命令行解析、模块整合、一键触发检测流程（唯一入口）。"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlparse

# 允许在项目根目录执行：python testcases/security/run_detector.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config.settings  # noqa: F401  触发统一日志 setup_logging

from config.settings import BASE_URL, TIMEOUT
from core.request_handler import RequestHandler
from testcases.security.auth_handler import AuthManager
from testcases.security.bug_logger import BugLogGenerator
from testcases.security.detector_core import SecurityDetector
from testcases.security.interface_config import get_all_interfaces, get_interface_config
from testcases.security.payload.payload_config import (
    SQL_INJECT_PAYLOADS,
    XSS_PAYLOADS,
    load_custom_payload,
)

logger = logging.getLogger(__name__)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """解析命令行参数（按项目架构文档仅保留两个可选参数）。"""
    parser = argparse.ArgumentParser(description="接口安全自动化检测（SQL 注入 / XSS）")
    parser.add_argument(
        "--interface",
        type=str,
        default=None,
        help="指定单接口检测（如 /login）；不指定则批量检测全部接口",
    )
    parser.add_argument(
        "--custom-payload",
        dest="custom_payload_path",
        type=str,
        default=None,
        help="自定义 payload txt 文件路径（按行读取，可混合 SQL/XSS）",
    )
    return parser.parse_args(argv)


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    """payload 去重并保序。"""
    seen = set()
    out: List[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def init_all_instances(
    custom_payload_path: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Tuple[RequestHandler, AuthManager, SecurityDetector]:
    """初始化 RequestHandler、AuthManager、SecurityDetector，并加载 payload（内置 + 自定义）。"""
    effective_base_url = base_url or BASE_URL
    request_handler = RequestHandler(base_url=effective_base_url)
    auth_manager = AuthManager(
        request_handler,
        username=os.environ.get("SECURITY_TEST_USERNAME"),
        password=os.environ.get("SECURITY_TEST_PASSWORD"),
    )
    try:
        auth_manager.get_token()
    except Exception:
        logger.exception("获取 Token 失败（将继续检测无需认证接口）")

    sql_payloads = _dedupe_preserve_order(list(SQL_INJECT_PAYLOADS))
    xss_payloads = _dedupe_preserve_order(list(XSS_PAYLOADS))

    if custom_payload_path:
        extra = load_custom_payload(custom_payload_path)
        sql_payloads = _dedupe_preserve_order(sql_payloads + extra)
        xss_payloads = _dedupe_preserve_order(xss_payloads + extra)

    detector = SecurityDetector(request_handler, auth_manager, sql_payloads, xss_payloads)
    logger.info("安全检测初始化完成：BASE_URL=%s TIMEOUT=%ss", effective_base_url, TIMEOUT)
    return request_handler, auth_manager, detector


def _build_interface_from_url(target_url: str) -> Tuple[str, Dict[str, Any]]:
    """将完整 URL 解析为 (base_url, interface_cfg)。

    说明：
        该能力用于靶场/训练环境快速探测：你只需传入目标 URL（可带 query 参数），模块会自动：
        - 提取 base_url（scheme://host[:port]）
        - 提取 path 作为 interface
        - 若 URL 自带 query 参数，则默认注入第一个 query key
    """
    parsed = urlparse(target_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"非法 URL：{target_url}")
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path or "/"

    qs = parse_qs(parsed.query, keep_blank_values=True)
    if qs:
        # 选择第一个 query key 作为默认注入点
        param_name = list(qs.keys())[0]
        default_val = qs.get(param_name, [""])[0]
        default_data = {param_name: default_val if default_val is not None else ""}
        param_type = "query"
    else:
        # 无 query 时给一个默认参数名，便于探测（实际接口可在 interface_config 中精配）
        default_data = {"q": "test"}
        param_type = "query"

    interface_cfg = {
        "interface": path,
        "method": "GET",
        "need_auth": False,
        "param_type": param_type,
        "default_data": default_data,
    }
    return base_url, interface_cfg


def run_detection(interface: Optional[str] = None, custom_payload_path: Optional[str] = None) -> list:
    """执行检测流程（单接口/批量），返回漏洞信息列表。

    兼容：
        - interface 为 /path：从 interface_config 中取配置
        - interface 为 http(s)://...：自动解析 URL 并构造单接口配置（训练/靶场便捷模式）
    """
    base_url: Optional[str] = None
    url_mode_cfg: Optional[Dict[str, Any]] = None

    if interface and (interface.startswith("http://") or interface.startswith("https://")):
        try:
            base_url, url_mode_cfg = _build_interface_from_url(interface)
        except Exception:
            logger.exception("解析目标 URL 失败：%s", interface)
            return []

    try:
        _client, _auth, detector = init_all_instances(custom_payload_path, base_url=base_url)
    except Exception:
        logger.exception("初始化检测实例失败")
        return []
    _ = (_client, _auth)

    if interface:
        cfg = url_mode_cfg or get_interface_config(interface)
        if not cfg:
            logger.error("接口配置不存在：%s", interface)
            return []
        detector.detect_single_interface(cfg)
        return list(detector.bug_info_list)

    configs = get_all_interfaces()
    detector.detect_all_interfaces(configs)
    return list(detector.bug_info_list)


def main(argv: Optional[Sequence[str]] = None) -> None:
    """主流程：检测 → 生成 Markdown Bug 日志 → 打印摘要。"""
    args = parse_args(argv)
    logger.info("开始安全检测：interface=%s custom_payload=%s", args.interface, args.custom_payload_path)

    try:
        bug_info_list = run_detection(args.interface, args.custom_payload_path)
    except Exception:
        logger.exception("检测流程异常，已降级为空结果")
        bug_info_list = []

    if bug_info_list:
        generator = BugLogGenerator(bug_info_list)
        path = generator.save_md_log()
        if path:
            logger.info("Bug 日志已保存：%s", path)
        BugLogGenerator.print_bug_summary(bug_info_list)
    else:
        logger.info("本次接口安全检测未发现任何SQL注入/XSS漏洞")


if __name__ == "__main__":
    main()

