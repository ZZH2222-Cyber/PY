# testcases/security/payload/payload_config.py
"""Payload 配置模块，管理 SQL 注入和 XSS 检测 payload。"""

import logging
from typing import List

logger = logging.getLogger(__name__)

# ==================== SQL 注入 Payload ====================

# SQL 注入 payload 列表，覆盖报错型、布尔盲注、参数拼接型等场景
SQL_INJECT_PAYLOADS: List[str] = [
    # ---------- 报错型注入 ----------
    "' OR 1=1 --",
    "' OR '1'='1",
    "1' OR '1'='1' --",
    "' OR 1=1#",
    "1' OR 1=1#",
    # 报错函数注入
    "and extractvalue(1,concat(0x7e,version(),0x7e))",
    "and updatexml(1,concat(0x7e,version(),0x7e),1)",
    "' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)",
    # ---------- 布尔盲注 ----------
    "' AND 1=1#",
    "' AND 1=2#",
    "' AND 1=1 --",
    "' AND 1=2 --",
    "1' AND 1=1 --",
    "1' AND 1=2 --",
    # ---------- 时间盲注 ----------
    "' AND SLEEP(5)#",
    "' AND BENCHMARK(10000000,SHA1('test'))#",
    # ---------- 参数拼接型注入 ----------
    "1; DROP TABLE IF EXISTS user;",
    "1; SELECT * FROM user;",
    "1 UNION SELECT 1,2,3 --",
    "1 UNION SELECT username,password FROM user --",
    # ---------- 注释符变体 ----------
    "'/**/OR/**/1=1/**/--",
    "'%20OR%20'1'='1",
]

# ==================== XSS Payload ====================

# XSS 跨站脚本 payload 列表，覆盖反射型、HTML 实体编码型等场景
XSS_PAYLOADS: List[str] = [
    # ---------- 反射型 XSS ----------
    "<script>alert('xss')</script>",
    "<script>alert(1)</script>",
    "<script>alert(document.cookie)</script>",
    "<img src=x onerror=alert(1)>",
    "<img src=1 onerror=alert('xss')>",
    "<svg onload=alert(1)>",
    "<body onload=alert(1)>",
    "<iframe src='javascript:alert(1)'>",
    "<input onfocus=alert(1) autofocus>",
    "<marquee onstart=alert(1)>",
    "<details open ontoggle=alert(1)>",
    # ---------- 事件处理型 ----------
    "\" onclick=alert(1) x=\"",
    "' onclick=alert(1) x='",
    "javascript:alert(1)",
    "JaVaScRiPt:alert(1)",
    # ---------- HTML 实体编码型 ----------
    "&lt;script&gt;alert(1)&lt;/script&gt;",
    "&#60;script&#62;alert(1)&#60;/script&#62;",
    "&#x3c;script&#x3e;alert(1)&#x3c;/script&#x3e;",
    # ---------- 大小写混淆 ----------
    "<ScRiPt>alert(1)</sCrIpT>",
    "<SCRIPT>alert(1)</SCRIPT>",
    # ---------- 空格/换行绕过 ----------
    "<script/src=x>alert(1)</script>",
    "<script\n>alert(1)</script>",
    "<script\t>alert(1)</script>",
    # ---------- 编码绕过 ----------
    "%3Cscript%3Ealert(1)%3C/script%3E",
    "\\x3cscript\\x3ealert(1)\\x3c/script\\x3e",
]


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
            # 逐行读取，过滤空行和注释行
            for line in f:
                line = line.strip()
                # 跳过空行和以 # 开头的注释行
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
