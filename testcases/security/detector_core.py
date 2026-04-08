"""安全检测核心：payload 注入、接口请求、漏洞启发式判断、漏洞信息收集。"""

import logging
import re
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Tuple

from requests import Response
from requests.exceptions import RequestException

from core.request_handler import RequestHandler
from testcases.security.auth_handler import AuthManager

logger = logging.getLogger(__name__)


class SecurityDetector:
    """安全检测器：对接口配置进行 SQL 注入与 XSS 自动化探测。"""

    def __init__(
        self,
        request_handler: RequestHandler,
        auth_manager: AuthManager,
        sql_payloads: List[str],
        xss_payloads: List[str],
    ) -> None:
        """初始化检测器。

        参数:
            request_handler: 原项目 RequestHandler。
            auth_manager: 认证管理器（可返回 Authorization 头）。
            sql_payloads: SQL 注入 payload 列表。
            xss_payloads: XSS payload 列表。
        """
        self._request_handler = request_handler
        self._auth_manager = auth_manager
        self._sql_payloads = list(sql_payloads)
        self._xss_payloads = list(xss_payloads)

        # 检测结果：标准化漏洞字典列表（供 BugLogGenerator 使用）
        self.bug_info_list: List[Dict[str, Any]] = []

    @staticmethod
    def _resolve_path(template: str, path_params: Dict[str, Any]) -> str:
        """将 Flask 风格路径模板转为真实路径。"""
        result = template
        for key, value in path_params.items():
            result = re.sub(rf"<int:{re.escape(key)}>", str(value), result)
            result = re.sub(rf"<{re.escape(key)}>", str(value), result)
        return result

    def _build_headers(self, need_auth: bool) -> Dict[str, str]:
        """按 need_auth 决定是否携带认证头。"""
        if not need_auth:
            return {}
        return self._auth_manager.build_auth_headers()

    def _dispatch_request(
        self,
        cfg: Dict[str, Any],
        param_name: str,
        payload: str,
    ) -> Tuple[Response, str]:
        """按接口配置发送请求，返回响应与最终路径。"""
        method = str(cfg["method"]).upper()
        interface = str(cfg["interface"])
        param_type = str(cfg["param_type"])
        defaults = deepcopy(cfg.get("default_data") or {})
        headers = self._build_headers(bool(cfg.get("need_auth")))

        if method == "GET":
            if param_type == "query":
                params = deepcopy(defaults)
                params[param_name] = payload
                url = self._resolve_path(interface, {}) if "<" in interface else interface
                return self._request_handler.get(url, params=params, headers=headers), url
            if param_type == "path":
                path_data = deepcopy(defaults)
                path_data[param_name] = payload
                url = self._resolve_path(interface, path_data)
                return self._request_handler.get(url, headers=headers), url
            raise ValueError(f"GET 不支持 param_type={param_type}")

        if method == "POST":
            url = interface
            if "<" in interface:
                url = self._resolve_path(interface, defaults)
            if param_type == "JSON":
                body = deepcopy(defaults)
                body[param_name] = payload
                return self._request_handler.post(url, json=body, headers=headers), url
            if param_type == "form":
                body = deepcopy(defaults)
                body[param_name] = payload
                return self._request_handler.post(url, data=body, headers=headers), url
            raise ValueError(f"POST 不支持 param_type={param_type}")

        raise ValueError(f"不支持的 method：{method}")

    @staticmethod
    def _heuristic_sql_vulnerable(response: Response) -> bool:
        """SQL 注入启发式：状态码异常 + 常见数据库错误片段。"""
        markers = (
            "sql syntax",
            "syntax error",
            "mysql",
            "sqlite",
            "postgresql",
            "ora-",
            "odbc",
            "sql server",
            "stack trace",
        )
        text = (response.text or "").lower()
        return response.status_code >= 400 and any(m in text for m in markers)

    @staticmethod
    def _heuristic_xss_vulnerable(response: Response, payload: str) -> bool:
        """XSS 启发式：响应正文回显 payload（需人工复核）。"""
        return bool(payload) and payload in (response.text or "")

    def _append_bug(
        self,
        vuln_type: str,
        risk_level: str,
        target_path: str,
        http_method: str,
        inject_param: str,
        payload: str,
        status_code: int,
        reason: str,
        response_snippet: str,
        error_message: str = "",
    ) -> None:
        """追加一条标准化漏洞信息（异常不应打断主流程）。"""
        try:
            self.bug_info_list.append(
                {
                    "vuln_type": vuln_type,
                    "risk_level": risk_level,
                    "target_path": target_path,
                    "http_method": http_method,
                    "inject_param": inject_param,
                    "payload": payload,
                    "status_code": status_code,
                    "reason": reason,
                    "response_snippet": response_snippet[:2000],
                    "error_message": error_message,
                }
            )
        except Exception:
            logger.exception("追加漏洞记录失败（已忽略）")

    def detect_single_interface(self, interface_cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
        """单接口检测：结果写入 bug_info_list 并返回。"""
        self.bug_info_list = []
        self._detect_interface_impl(interface_cfg)
        return list(self.bug_info_list)

    def detect_all_interfaces(self, interfaces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量检测：单接口异常记录日志后继续。"""
        self.bug_info_list = []
        for cfg in interfaces:
            try:
                self._detect_interface_impl(cfg)
            except Exception:
                logger.exception("接口检测异常已跳过：%s %s", cfg.get("method"), cfg.get("interface"))
        return list(self.bug_info_list)

    def _detect_interface_impl(self, interface_cfg: Dict[str, Any]) -> None:
        """对单条接口配置执行检测（内部异常不应传播到批量层）。"""
        method = str(interface_cfg.get("method", "")).upper()
        interface = str(interface_cfg.get("interface", ""))

        # 默认对 default_data 中的所有字段尝试注入
        param_names = list((interface_cfg.get("default_data") or {}).keys())
        if not param_names:
            logger.info("接口无可注入参数，跳过：%s %s", method, interface)
            return

        for param_name in param_names:
            for payload in self._sql_payloads:
                self._probe(interface_cfg, param_name, payload, "SQL_INJECTION")
            for payload in self._xss_payloads:
                self._probe(interface_cfg, param_name, payload, "XSS")

    def _probe(self, cfg: Dict[str, Any], param_name: str, payload: str, vuln_type: str) -> None:
        """注入单个 payload 并判定；失败记录 DETECTION_ERROR，不中断流程。"""
        method = str(cfg.get("method", "")).upper()
        interface = str(cfg.get("interface", ""))
        try:
            response, target_path = self._dispatch_request(cfg, param_name, payload)
        except (RequestException, ValueError) as exc:
            self._append_bug(
                vuln_type="DETECTION_ERROR",
                risk_level="中危",
                target_path=interface,
                http_method=method,
                inject_param=param_name,
                payload=payload,
                status_code=0,
                reason="请求失败或参数不合法，未完成该次探测",
                response_snippet="",
                error_message=str(exc),
            )
            return
        except Exception as exc:
            self._append_bug(
                vuln_type="DETECTION_ERROR",
                risk_level="中危",
                target_path=interface,
                http_method=method,
                inject_param=param_name,
                payload=payload,
                status_code=0,
                reason="派发请求阶段发生未预期异常",
                response_snippet="",
                error_message=str(exc),
            )
            logger.exception("派发请求未预期异常：%s", exc)
            return

        snippet = (response.text or "")[:2000]
        if vuln_type == "SQL_INJECTION" and self._heuristic_sql_vulnerable(response):
            self._append_bug(
                vuln_type="SQL_INJECTION",
                risk_level="高危",
                target_path=target_path,
                http_method=method,
                inject_param=param_name,
                payload=payload,
                status_code=response.status_code,
                reason="响应包含典型 SQL/堆栈错误特征，需人工复核",
                response_snippet=snippet,
            )
        elif vuln_type == "XSS" and self._heuristic_xss_vulnerable(response, payload):
            self._append_bug(
                vuln_type="XSS",
                risk_level="中危",
                target_path=target_path,
                http_method=method,
                inject_param=param_name,
                payload=payload,
                status_code=response.status_code,
                reason="响应回显 payload，可能存在反射型 XSS，需人工复核",
                response_snippet=snippet,
            )

