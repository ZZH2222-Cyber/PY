# testcases/security/payload/payload_config.py
"""Payload 配置模块，管理 SQL 注入和 XSS 检测 payload。"""

import json
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

PAYLOAD_DB_PATH = Path(__file__).resolve().parents[3] / "data" / "security_payloads.json"


def _load_payloads_from_db() -> tuple:
    """从JSON数据库加载所有payload。"""
    sql_payloads = []
    xss_payloads = []

    if PAYLOAD_DB_PATH.exists():
        try:
            with open(PAYLOAD_DB_PATH, 'r', encoding='utf-8') as f:
                db = json.load(f)

            sql_db = db.get("sql_injection", {})
            xss_db = db.get("xss", {})

            for db_type, payloads in sql_db.get("error_based", {}).items():
                sql_payloads.extend([p["payload"] for p in payloads])

            for db_type, payloads in sql_db.get("boolean_based", {}).items():
                sql_payloads.extend([p["payload"] for p in payloads])

            for db_type, payloads in sql_db.get("time_based", {}).items():
                sql_payloads.extend([p["payload"] for p in payloads])

            for db_type, payloads in sql_db.get("union_based", {}).items():
                sql_payloads.extend([p["payload"] for p in payloads])

            for db_type, payloads in sql_db.get("stacked_queries", {}).items():
                sql_payloads.extend([p["payload"] for p in payloads])

            for category, payloads in xss_db.get("reflected", {}).items():
                xss_payloads.extend([p["payload"] for p in payloads])

            for category, payloads in xss_db.get("dom_based", {}).items():
                xss_payloads.extend([p["payload"] for p in payloads])

            for category, payloads in xss_db.get("stored", {}).items():
                xss_payloads.extend([p["payload"] for p in payloads])

            logger.info(f"从数据库加载了 {len(sql_payloads)} 条SQL注入payload和 {len(xss_payloads)} 条XSS payload")

        except Exception as e:
            logger.error(f"加载payload数据库失败: {e}")

    return sql_payloads, xss_payloads


_extracted_sql, _extracted_xss = _load_payloads_from_db()

# ==================== SQL 注入 Payload ====================

SQL_INJECT_PAYLOADS: List[str] = [
    # ---------- 基础报错型注入 ----------
    "' OR 1=1 --",
    "' OR '1'='1",
    "1' OR '1'='1' --",
    "' OR 1=1#",
    "1' OR 1=1#",
    # ---------- 报错注入函数 ----------
    "and extractvalue(1,concat(0x7e,version(),0x7e))",
    "and updatexml(1,concat(0x7e,version(),0x7e),1)",
    "' AND EXTRACTVALUE(1,CONCAT(0x7e,VERSION())) -- ",
    "' AND UPDATEXML(1,CONCAT(0x7e,VERSION()),1) -- ",
    # ---------- 联合查询注入 ----------
    "1 UNION SELECT 1,2,3 --",
    "1 UNION SELECT NULL,NULL,NULL --",
    "' UNION SELECT NULL,NULL,VERSION() -- ",
    "' UNION SELECT 1,2,3 FROM information_schema.tables -- ",
    # ---------- 布尔盲注 ----------
    "' AND 1=1#",
    "' AND 1=2#",
    "' AND 1=1 --",
    "' AND 1=2 --",
    "1' AND 1=1 --",
    "1' AND 1=2 --",
    "admin' AND 1=1 -- ",
    "admin' AND 1=2 -- ",
    # ---------- 时间盲注 ----------
    "' AND SLEEP(5)#",
    "' AND BENCHMARK(10000000,SHA1('test'))#",
    "1' AND SLEEP(3) -- ",
    "'; SELECT SLEEP(5) -- ",
    # ---------- 参数拼接型注入 ----------
    "1; DROP TABLE IF EXISTS user;",
    "1; SELECT * FROM user;",
    "1 UNION SELECT username,password FROM user --",
    # ---------- 注释符变体 ----------
    "'/**/OR/**/1=1/**/--",
    "'%20OR%20'1'='1",
] + _extracted_sql if _extracted_sql else []

# ==================== XSS Payload ====================

XSS_PAYLOADS: List[str] = [
    # ---------- 基础反射型 ----------
    "<script>alert('xss')</script>",
    "<script>alert(1)</script>",
    "<script>alert(document.cookie)</script>",
    "\"><script>alert(1)</script>",
    "'><script>alert(1)</script>",
    "><script>alert(1)</script>",
    # ---------- 事件处理型 ----------
    "<img src=x onerror=alert(1)>",
    "<img src=1 onerror=alert('xss')>",
    "<svg onload=alert(1)>",
    "<body onload=alert(1)>",
    "<iframe src='javascript:alert(1)'>",
    "<input onfocus=alert(1) autofocus>",
    "<select onfocus=alert(1) autofocus>",
    "<textarea onfocus=alert(1) autofocus>",
    "<keygen onfocus=alert(1) autofocus>",
    "<video><source onerror=alert(1)>",
    "<audio src=x onerror=alert(1)>",
    "<marquee onstart=alert(1)>",
    "<meter onmouseover=alert(1)>0</meter>",
    "<details open ontoggle=alert(1)>",
    "<iframe onload=alert(1)>",
    "<object data=x onerror=alert(1)>",
    "<embed src=x onerror=alert(1)>",
    # ---------- 伪协议 ----------
    "javascript:alert(1)",
    "<a href=javascript:alert(1)>click</a>",
    "<svg><script>alert(1)</script></svg>",
    # ---------- HTML实体编码 ----------
    "&lt;script&gt;alert(1)&lt;/script&gt;",
    "&#60;script&#62;alert(1)&#60;/script&#62;",
    # ---------- 大小写混淆 ----------
    "<ScRiPt>alert(1)</sCrIpT>",
    "<SCRIPT>alert(1)</SCRIPT>",
    # ---------- 编码绕过 ----------
    "%3Cscript%3Ealert(1)%3C/script%3E",
    "\\x3cscript\\x3ealert(1)\\x3c/script\\x3e",
] + _extracted_xss if _extracted_xss else []


def load_custom_payload(file_path: str) -> List[str]:
    """从本地文件加载自定义 payload。

    参数：
        file_path: payload 文件的绝对路径或相对路径。

    返回：
        payload 列表，每行一个 payload；若读取失败则返回空列表。

    异常：
        无（异常会被捕获并记录日志）。
    """
    payloads: List[str] = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    payloads.append(line)

        logger.info("成功加载自定义 payload，共 %d 条，文件路径：%s", len(payloads), file_path)

    except FileNotFoundError:
        logger.error("payload 文件不存在：%s", file_path)
    except PermissionError:
        logger.error("无权限读取 payload 文件：%s", file_path)
    except UnicodeDecodeError as e:
        logger.error("payload 文件编码错误：%s，错误：%s", file_path, e)
    except OSError as e:
        logger.error("读取 payload 文件失败：%s，错误：%s", file_path, e)

    return payloads