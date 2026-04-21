"""安全检测核心：payload 注入、接口请求、可解释证据提取、漏洞信息收集。

说明：
    本模块只做"探测与证据记录"，不包含任何数据提取/外带逻辑。
    适用于合法靶场/训练环境的安全测试与可解释报告输出。
"""

import json
import logging
import os
import re
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from requests import Response
from requests.exceptions import RequestException

from core.request_handler import RequestHandler
from testcases.security.auth_handler import AuthManager

logger = logging.getLogger(__name__)

PAYLOAD_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "security_payloads.json"


def load_payload_db() -> Dict[str, Any]:
    """从data/security_payloads.json加载所有payload数据。"""
    if PAYLOAD_DB_PATH.exists():
        try:
            with open(PAYLOAD_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


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
        self._payload_db = load_payload_db()

        self.bug_info_list: List[Dict[str, Any]] = []
        self._sql_error_markers: Tuple[str, ...] = (
            "sql syntax",
            "syntax error",
            "mysql",
            "sqlite",
            "postgresql",
            "psycopg2",
            "ora-",
            "odbc",
            "sql server",
            "stack trace",
            "traceback",
            "xp_",
            "extractvalue",
            "updatexml",
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

    def _detect_injection_type(self, cfg: Dict[str, Any], param_name: str) -> str:
        """探测注入点类型：字符型、数字型、JSON型。"""
        interface = str(cfg.get("interface", ""))
        method = str(cfg.get("method", "")).upper()

        test_chars = [
            ("'", "sql_error"),
            ("1", "numeric"),
            ('"', "json_string"),
        ]

        for test_val, test_type in test_chars:
            try:
                response, _ = self._dispatch_request(cfg, param_name, test_val)
                text = (response.text or "").lower()

                if test_type == "sql_error":
                    if any(m in text for m in self._sql_error_markers):
                        return "error_based"
                elif test_type == "numeric":
                    if response.status_code == 200 and test_val in text:
                        return "numeric"
                elif test_type == "json_string":
                    if response.status_code == 200 and '"' in response.text:
                        return "json"
            except Exception:
                pass

        return "unknown"

    def _detect_time_blind_injection(self, cfg: Dict[str, Any], param_name: str) -> Optional[Dict[str, Any]]:
        """检测时间盲注：发送带有延时的payload，比较响应时间差异。"""
        payload_db = self._payload_db.get("sql_injection", {}).get("time_based", {})

        for db_type, payloads in payload_db.items():
            for payload_entry in payloads[:3]:
                payload = payload_entry.get("payload", "")
                if not payload:
                    continue

                try:
                    start_time = time.time()
                    test_resp, _ = self._dispatch_request(cfg, param_name, payload)
                    elapsed_time = time.time() - start_time

                    if elapsed_time > 3:
                        return {
                            "type": "time_based",
                            "payload": payload,
                            "db_type": db_type,
                            "delay": elapsed_time,
                            "evidence": f"响应延迟 {elapsed_time:.2f}秒"
                        }
                except Exception:
                    pass

        return None

    def _detect_path_traversal(self, cfg: Dict[str, Any], param_name: str) -> Optional[Dict[str, Any]]:
        """检测路径遍历漏洞：尝试读取系统敏感文件。"""
        path_payloads = self._payload_db.get("path_traversal", {})
        common_files = [
            ("/etc/passwd", "root:x:"),
            ("C:\\Windows\\win.ini", "[extensions]"),
            ("/etc/hosts", "localhost"),
            ("/proc/self/environ", "PATH"),
        ]

        for os_type, payloads in path_payloads.items():
            if os_type == "description":
                continue
            if not isinstance(payloads, list):
                continue
            for payload_entry in payloads[:5]:
                if not isinstance(payload_entry, dict):
                    continue
                payload = payload_entry.get("payload", "")
                if not payload:
                    continue

                try:
                    response, _ = self._dispatch_request(cfg, param_name, payload)
                    text = response.text or ""

                    for file_path, expected_content in common_files:
                        if expected_content.lower() in text.lower():
                            return {
                                "type": "path_traversal",
                                "payload": payload,
                                "target_file": file_path,
                                "evidence": f"成功读取敏感文件 {file_path}"
                            }
                except Exception:
                    pass

        return None

    def _detect_command_injection(self, cfg: Dict[str, Any], param_name: str) -> Optional[Dict[str, Any]]:
        """检测命令注入漏洞：尝试执行系统命令。"""
        cmd_payloads = self._payload_db.get("command_injection", {})

        for os_type, payloads in cmd_payloads.items():
            if os_type == "description":
                continue
            if not isinstance(payloads, list):
                continue
            for payload_entry in payloads[:5]:
                if not isinstance(payload_entry, dict):
                    continue
                payload = payload_entry.get("payload", "")
                if not payload:
                    continue

                try:
                    response, _ = self._dispatch_request(cfg, param_name, payload)
                    text = response.text or ""

                    cmd_indicators = ["root:x:", "uid=", "Directory of", "User accounts", "total", "Windows IP", "Microsoft"]
                    for indicator in cmd_indicators:
                        if indicator.lower() in text.lower():
                            return {
                                "type": "command_injection",
                                "payload": payload,
                                "os_type": os_type,
                                "evidence": f"命令执行成功，响应包含: {indicator}"
                            }
                except Exception:
                    pass

        return None

    def _detect_boolean_blind_injection(self, cfg: Dict[str, Any], param_name: str) -> Optional[Dict[str, Any]]:
        """检测布尔盲注：比较注入永真式和永假式的响应差异。"""
        payload_db = self._payload_db.get("sql_injection", {}).get("boolean_based", {})

        try:
            baseline_resp, _ = self._dispatch_request(cfg, param_name, "test")
            baseline_len = len(baseline_resp.text or "")
            baseline_status = baseline_resp.status_code

            true_payloads = [
                "' OR 1=1 -- ",
                "' AND 1=1 -- ",
                "1' OR '1'='1' -- ",
            ]
            false_payloads = [
                "' AND 1=2 -- ",
                "' OR 1=2 -- ",
                "1' AND '1'='2' -- ",
            ]

            for true_payload in true_payloads:
                for false_payload in false_payloads:
                    try:
                        true_resp, _ = self._dispatch_request(cfg, param_name, true_payload)
                        false_resp, _ = self._dispatch_request(cfg, param_name, false_payload)

                        true_len = len(true_resp.text or "")
                        false_len = len(false_resp.text or "")

                        if abs(true_len - false_len) > 50:
                            return {
                                "type": "boolean_based",
                                "true_payload": true_payload,
                                "false_payload": false_payload,
                                "true_length": true_len,
                                "false_length": false_len,
                                "evidence": f"响应长度差异: {abs(true_len - false_len)} bytes"
                            }
                    except Exception:
                        pass
        except Exception:
            pass

        return None

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

        param_names = list((interface_cfg.get("default_data") or {}).keys())
        if not param_names:
            logger.info("接口无可注入参数，跳过：%s %s", method, interface)
            return

        for param_name in param_names:
            baseline_value = str((interface_cfg.get("default_data") or {}).get(param_name, "test"))
            baseline_resp = self._try_request(interface_cfg, param_name, baseline_value)
            baseline_metrics = self._response_metrics(baseline_resp) if baseline_resp else {"status_code": 0, "length": 0}

            injection_type = self._detect_injection_type(interface_cfg, param_name)

            for payload in self._sql_payloads:
                self._probe(interface_cfg, param_name, payload, "SQL_INJECTION", baseline_metrics)

            for payload in self._xss_payloads:
                self._probe(interface_cfg, param_name, payload, "XSS", baseline_metrics)

            if injection_type != "unknown":
                time_blind_result = self._detect_time_blind_injection(interface_cfg, param_name)
                if time_blind_result:
                    self._append_bug(
                        vuln_type="SQL_INJECTION_TIME_BLIND",
                        risk_level="高危",
                        target_path=interface,
                        http_method=method,
                        inject_param=param_name,
                        payload=time_blind_result.get("payload", ""),
                        status_code=0,
                        reason=f"时间盲注检测: {time_blind_result.get('evidence', '')}",
                        response_snippet="",
                        error_message="",
                    )

                bool_blind_result = self._detect_boolean_blind_injection(interface_cfg, param_name)
                if bool_blind_result:
                    self._append_bug(
                        vuln_type="SQL_INJECTION_BOOLEAN_BLIND",
                        risk_level="高危",
                        target_path=interface,
                        http_method=method,
                        inject_param=param_name,
                        payload=bool_blind_result.get("true_payload", ""),
                        status_code=0,
                        reason=f"布尔盲注检测: {bool_blind_result.get('evidence', '')}",
                        response_snippet="",
                        error_message="",
                    )

            path_traversal_result = self._detect_path_traversal(interface_cfg, param_name)
            if path_traversal_result:
                self._append_bug(
                    vuln_type="PATH_TRAVERSAL",
                    risk_level="高危",
                    target_path=interface,
                    http_method=method,
                    inject_param=param_name,
                    payload=path_traversal_result.get("payload", ""),
                    status_code=0,
                    reason=f"路径遍历检测: {path_traversal_result.get('evidence', '')}",
                    response_snippet="",
                    error_message="",
                )

            cmd_injection_result = self._detect_command_injection(interface_cfg, param_name)
            if cmd_injection_result:
                self._append_bug(
                    vuln_type="COMMAND_INJECTION",
                    risk_level="严重",
                    target_path=interface,
                    http_method=method,
                    inject_param=param_name,
                    payload=cmd_injection_result.get("payload", ""),
                    status_code=0,
                    reason=f"命令注入检测: {cmd_injection_result.get('evidence', '')}",
                    response_snippet="",
                    error_message="",
                )

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

