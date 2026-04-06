# config/settings.py
"""项目配置文件：全局常量、路径与日志初始化。"""

import logging
import os
from pathlib import Path
from typing import List

# ---------------------------------------------------------------------------
# 路径（PROJECT_ROOT 为项目根目录）
# ---------------------------------------------------------------------------
PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR: str = os.path.join(PROJECT_ROOT, "data")
REPORT_DIR: str = os.path.join(PROJECT_ROOT, "reports")
LOG_DIR: str = os.path.join(PROJECT_ROOT, "logs")

# ---------------------------------------------------------------------------
# HTTP 默认配置（可通过环境变量覆盖，便于 CI / 多环境）
# ---------------------------------------------------------------------------
BASE_URL: str = os.environ.get("BASE_URL", "https://httpbin.org")
REQUEST_TIMEOUT: int = int(os.environ.get("REQUEST_TIMEOUT", "10"))

# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------
LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT: str = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
LOG_FILE: str = os.path.join(LOG_DIR, "test.log")

# ---------------------------------------------------------------------------
# 敏感字段（日志脱敏）
# ---------------------------------------------------------------------------
SENSITIVE_KEYS: List[str] = [
    "password",
    "pwd",
    "token",
    "secret",
    "apikey",
    "api_key",
    "authorization",
    "access_token",
    "refresh_token",
]

# DeepSeek（AI 用例生成，可选）
DEEPSEEK_API_KEY: str = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL: str = os.environ.get(
    "DEEPSEEK_API_URL",
    "https://api.deepseek.com/v1/chat/completions",
)


def _resolve_log_level(level_name: str) -> int:
    """将日志级别名称解析为 logging 模块使用的整型级别。

    参数:
        level_name: 如 "INFO"、"DEBUG"。

    返回:
        logging 级别常量。

    异常:
        无。
    """
    return getattr(logging, level_name.upper(), logging.INFO)


def setup_logging() -> None:
    """配置根日志：同时输出到控制台与 logs/test.log。

    参数:
        无。

    返回:
        无。

    异常:
        OSError: 无法创建日志目录或日志文件时抛出。
    """
    try:
        Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        logging.error("无法创建日志目录：%s，错误：%s", LOG_DIR, exc)
        raise

    level = _resolve_log_level(LOG_LEVEL)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except OSError as exc:
        logging.error("无法创建日志文件：%s，错误：%s", LOG_FILE, exc)
        raise

    logging.info("日志系统初始化完成，级别=%s", LOG_LEVEL)


# 导入本模块时初始化日志（测试与脚本均可直接 import config.settings）
setup_logging()
