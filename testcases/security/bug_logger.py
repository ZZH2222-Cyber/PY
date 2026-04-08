"""Bug 日志生成模块：将漏洞信息列表生成为 Markdown，并保存到 docs/security_bug_log/。"""

import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List

from config.settings import PROJECT_ROOT, SECURITY_BUG_LOG_DIR, SENSITIVE_KEYS

logger = logging.getLogger(__name__)


class BugLogGenerator:
    """生成并保存安全检测 Bug 日志（Markdown）。"""

    def __init__(self, bug_info_list: list) -> None:
        """初始化生成器。

        参数:
            bug_info_list: 漏洞信息列表（标准化字典）。
        """
        self.bug_info_list: List[Dict[str, Any]] = list(bug_info_list) if bug_info_list else []
        self.log_dir: str = SECURITY_BUG_LOG_DIR
        self.detect_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __create_log_dir(self) -> bool:
        """创建日志目录（失败返回 False，不抛异常）。"""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            return True
        except OSError as exc:
            logger.error("创建日志目录失败：%s，错误：%s", self.log_dir, exc, exc_info=True)
            return False
        except Exception:
            logger.exception("创建日志目录未预期异常：%s", self.log_dir)
            return False

    def __classify_vul_count(self) -> Dict[str, int]:
        """统计漏洞数量（总数、SQL 注入、XSS、高危、中危）。"""
        total = len(self.bug_info_list)
        sql_inject = sum(1 for r in self.bug_info_list if str(r.get("vuln_type", "")).upper() == "SQL_INJECTION")
        xss = sum(1 for r in self.bug_info_list if str(r.get("vuln_type", "")).upper() == "XSS")
        high_risk = sum(1 for r in self.bug_info_list if r.get("risk_level") == "高危")
        medium_risk = sum(1 for r in self.bug_info_list if r.get("risk_level") == "中危")
        return {
            "total": total,
            "sql_inject": sql_inject,
            "xss": xss,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
        }

    @staticmethod
    def _mask_text(text: str) -> str:
        """去敏：替换常见敏感字段片段，避免在报告中泄露 token/password。"""
        if not text:
            return ""
        masked = str(text)
        for key in SENSITIVE_KEYS:
            masked = re.sub(rf"(?i)({re.escape(key)})\\s*[:=]\\s*\\S+", r"\\1=******", masked)
        masked = re.sub(r"(?i)(bearer\\s+)[a-z0-9\\-_.]+", r"\\1******", masked)
        return masked

    def generate_md_content(self) -> str:
        """生成 Markdown 内容（符合项目文档规范）。"""
        stats = self.__classify_vul_count()
        interface_count = len({(r.get("http_method"), r.get("target_path")) for r in self.bug_info_list})

        lines: List[str] = [
            f"# 接口自动化安全检测Bug日志_{self.detect_time}",
            "",
            "## 检测概览",
            "",
            f"- **检测时间**：{self.detect_time}",
            f"- **检测接口总数**：{interface_count}",
            (
                f"- **漏洞统计**：total={stats['total']}，sql_inject={stats['sql_inject']}，xss={stats['xss']}，"
                f"high_risk={stats['high_risk']}，medium_risk={stats['medium_risk']}"
            ),
            "- **日志说明**：本日志由安全检测模块自动生成，内容已做脱敏与截断处理。",
            "",
            "## 漏洞详情表",
            "",
        ]

        cols = [
            "risk_level",
            "vuln_type",
            "http_method",
            "target_path",
            "inject_param",
            "payload",
            "status_code",
            "reason",
        ]
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("| " + " | ".join(["---"] * len(cols)) + " |")

        def _risk_weight(level: str) -> int:
            return {"高危": 3, "中危": 2, "低危": 1}.get(level, 0)

        rows = sorted(self.bug_info_list, key=lambda r: _risk_weight(str(r.get("risk_level", ""))), reverse=True)
        for row in rows:
            cells = []
            for key in cols:
                value = self._mask_text(str(row.get(key, "")))
                value = value.replace("|", "\\|").replace("\n", "<br>")
                cells.append(value)
            lines.append("| " + " | ".join(cells) + " |")

        lines.extend(
            [
                "",
                "## 通用修复建议",
                "",
                "### SQL 注入",
                "- 使用参数化查询（预编译语句 / ORM 绑定参数），避免直接拼接 SQL。",
                "- 最小权限原则配置数据库账号，限制多语句执行与危险函数。",
                "",
                "### XSS（跨站脚本）",
                "- 对用户输入做 HTML 转义（按输出上下文选择合适编码）。",
                "- 过滤危险标签与事件属性（如 script、onerror、javascript:），必要时启用 CSP。",
                "",
                "## 备注",
                "",
                "- 本日志由接口自动化安全检测子模块生成；请结合服务端日志与业务规则进行人工复核。",
                f"- 原项目文档目录：`{os.path.join(PROJECT_ROOT, 'docs')}`",
                "",
            ]
        )
        return "\n".join(lines)

    def save_md_log(self) -> str:
        """保存 Markdown 日志文件，成功返回绝对路径，失败返回空字符串。"""
        if not self.__create_log_dir():
            return ""

        filename = f"security_bug_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        full_path = os.path.abspath(os.path.join(self.log_dir, filename))
        try:
            content = self.generate_md_content()
            with open(full_path, "w", encoding="utf-8") as fp:
                fp.write(content)
            logger.info("已保存安全 Bug 日志：%s", full_path)
            return full_path
        except OSError as exc:
            logger.error("写入日志失败：%s，错误：%s", full_path, exc, exc_info=True)
            return ""
        except Exception:
            logger.exception("保存日志未预期异常：%s", full_path)
            return ""

    @staticmethod
    def print_bug_summary(bug_info_list: list) -> None:
        """打印检测摘要（走统一 logging）。"""
        try:
            rows = list(bug_info_list) if bug_info_list else []
            total = len(rows)
            high_risk = sum(1 for r in rows if r.get("risk_level") == "高危")
            medium_risk = sum(1 for r in rows if r.get("risk_level") == "中危")
            interfaces = sorted({(r.get("http_method"), r.get("target_path")) for r in rows})
            logger.info("安全检测摘要：total=%s high=%s medium=%s 接口数=%s", total, high_risk, medium_risk, len(interfaces))
            if interfaces:
                logger.info("涉及接口（去重）：%s", ", ".join(f"{m} {p}" for m, p in interfaces[:30]))
        except Exception:
            logger.exception("打印检测摘要异常")


if __name__ == "__main__":
    import config.settings  # noqa: F401  触发日志

    demo = [
        {
            "vuln_type": "SQL_INJECTION",
            "risk_level": "高危",
            "target_path": "/user/1",
            "http_method": "GET",
            "inject_param": "id",
            "payload": "' OR 1=1 --",
            "status_code": 500,
            "reason": "响应包含 SQL 报错特征（示例）",
            "response_snippet": "sql syntax error ...",
            "error_message": "",
        }
    ]
    gen = BugLogGenerator(demo)
    path = gen.save_md_log()
    BugLogGenerator.print_bug_summary(demo)
    logger.info("demo 日志：%s", path)

