"""安全检测核心：payload 注入、接口请求、可解释证据提取、漏洞信息收集。

说明：
    本模块只做“探测与证据记录”，不包含任何数据提取/外带逻辑。
    适用于合法靶场/训练环境的安全测试与可解释报告输出。
"""

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
        # SQL 错误关键字：用于证据与数据库指纹推断
        self._sql_error_markers: Tuple[str, ...] = (
            "sql syntax",
            "syntax error",
            "mysql",
            "sqlite",
            "postgresql",
            "psycopg2",
            "pymysql",
            "ora-",
            "odbc",
            "sql server",
            "stack trace",
            "traceback",
        )

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
        text = (response.text or "").lower()
        return response.status_code >= 400 and any(m in text for m in (
            "sql syntax",
            "syntax error",
            "mysql",
            "sqlite",
            "postgresql",
            "ora-",
            "odbc",
            "sql server",
            "stack trace",
            "traceback",
        ))

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

    @staticmethod
    def _response_metrics(response: Response) -> Dict[str, Any]:
        """提取响应的可对比指标（用于基线差异）。"""
        try:
            text = response.text or ""
        except Exception:
            text = ""
        return {
            "status_code": int(getattr(response, "status_code", 0) or 0),
            "length": len(text),
        }

    def _infer_db_fingerprint(self, body_lower: str) -> str:
        """根据报错关键字推断数据库/驱动类型（仅推断，用于报告解释）。"""
        if "mysql" in body_lower or "pymysql" in body_lower:
            return "MySQL"
        if "sqlite" in body_lower:
            return "SQLite"
        if "postgresql" in body_lower or "psycopg2" in body_lower:
            return "PostgreSQL"
        if "ora-" in body_lower:
            return "Oracle"
        if "sql server" in body_lower or "odbc" in body_lower:
            return "SQLServer"
        return "Unknown"

    def _extract_sql_evidence(self, text: str) -> Tuple[str, str, str]:
        """提取 SQL 报错证据：类型、细节、数据库指纹。"""
        lower = (text or "").lower()
        hits = [m for m in self._sql_error_markers if m in lower]
        if not hits:
            return "", "", ""
        fingerprint = self._infer_db_fingerprint(lower)
        detail = ",".join(hits[:5])
        return "db_error_marker", detail, fingerprint

    @staticmethod
    def _build_diff_hint(baseline: Dict[str, Any], current: Dict[str, Any]) -> str:
        """构建基线差异提示（不暴露敏感内容）。"""
        try:
            base_status = baseline.get("status_code")
            cur_status = current.get("status_code")
            base_len = baseline.get("length")
            cur_len = current.get("length")
            return f"status {base_status}->{cur_status}; len {base_len}->{cur_len}"
        except Exception:
            return ""

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
            # 基线请求：使用默认值，不做注入，用于差异对比解释
            baseline_value = str((interface_cfg.get("default_data") or {}).get(param_name, "test"))
            baseline_resp = self._try_request(interface_cfg, param_name, baseline_value)
            baseline_metrics = self._response_metrics(baseline_resp) if baseline_resp else {"status_code": 0, "length": 0}

            for payload in self._sql_payloads:
                self._probe(interface_cfg, param_name, payload, "SQL_INJECTION", baseline_metrics)
            for payload in self._xss_payloads:
                self._probe(interface_cfg, param_name, payload, "XSS", baseline_metrics)

    def _try_request(self, cfg: Dict[str, Any], param_name: str, payload: str) -> Optional[Response]:
        """发起一次请求（用于基线或探测）；异常返回 None。"""
        try:
            response, _target_path = self._dispatch_request(cfg, param_name, payload)
            return response
        except Exception:
            return None

    def _probe(
        self,
        cfg: Dict[str, Any],
        param_name: str,
        payload: str,
        vuln_type: str,
        baseline_metrics: Dict[str, Any],
    ) -> None:
        """注入单个 payload 并判定；记录可解释证据（基线差异/命中关键字）。"""
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

        body = response.text or ""
        snippet = body[:2000]
        current_metrics = self._response_metrics(response)
        diff_hint = self._build_diff_hint(baseline_metrics, current_metrics)

        if vuln_type == "SQL_INJECTION" and self._heuristic_sql_vulnerable(response):
            evidence_type, evidence_detail, db_fp = self._extract_sql_evidence(body)
            self._append_bug(
                vuln_type="SQL_INJECTION",
                risk_level="高危",
                target_path=target_path,
                http_method=method,
                inject_param=param_name,
                payload=payload,
                status_code=response.status_code,
                reason=f"命中 SQL 错误特征（{diff_hint}）",
                response_snippet=snippet,
                error_message="",
            )
            # 追加解释字段（不影响旧表头兼容）
            self.bug_info_list[-1].update(
                {
                    "evidence_type": evidence_type,
                    "evidence_detail": evidence_detail,
                    "db_fingerprint": db_fp,
                    "diff_hint": diff_hint,
                    "baseline_status_code": baseline_metrics.get("status_code", 0),
                    "baseline_length": baseline_metrics.get("length", 0),
                    "response_length": current_metrics.get("length", 0),
                }
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
                reason=f"命中回显特征（{diff_hint}）",
                response_snippet=snippet,
                error_message="",
            )
            self.bug_info_list[-1].update(
                {
                    "evidence_type": "reflected_payload",
                    "evidence_detail": "payload_reflected",
                    "db_fingerprint": "",
                    "diff_hint": diff_hint,
                    "baseline_status_code": baseline_metrics.get("status_code", 0),
                    "baseline_length": baseline_metrics.get("length", 0),
                    "response_length": current_metrics.get("length", 0),
                }
            )

