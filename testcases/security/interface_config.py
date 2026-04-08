"""接口配置模块：维护待检测接口清单与查询方法（仅配置，不包含检测逻辑）。"""

import copy
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# 待检测接口清单（按项目自研后端接口示例配置，可按实际业务增删改）
TARGET_INTERFACES: List[Dict[str, Any]] = [
    {
        # 登录：JSON 体提交账号密码，无需 Bearer
        "interface": "/login",
        "method": "POST",
        "need_auth": False,
        "param_type": "JSON",
        "default_data": {"username": "admin", "password": "123456"},
    },
    {
        # 用户查询：路径参数 user_id，需 Bearer Token
        "interface": "/user/<int:id>",
        "method": "GET",
        "need_auth": True,
        "param_type": "path",
        "default_data": {"id": 1},
    },
    {
        # 示例查询接口：用于演示 query 参数注入（对接真实业务时请替换为你的接口）
        "interface": "/get",
        "method": "GET",
        "need_auth": False,
        "param_type": "query",
        "default_data": {"q": "test"},
    },
]


def get_interface_config(interface: str) -> Dict[str, Any]:
    """按接口路径查询配置字典。

    参数:
        interface: 接口路径字符串，如 /login。

    返回:
        匹配成功返回配置字典深拷贝；失败返回空字典。
    """
    try:
        for item in TARGET_INTERFACES:
            if item.get("interface") == interface:
                return copy.deepcopy(item)
        logger.info("未找到接口配置：%s", interface)
        return {}
    except Exception:
        logger.exception("查询接口配置异常：%s", interface)
        return {}


def get_all_interfaces() -> List[Dict[str, Any]]:
    """获取全部接口配置（深拷贝），避免外部修改常量。"""
    try:
        return copy.deepcopy(TARGET_INTERFACES)
    except Exception:
        logger.exception("获取全部接口配置失败")
        return []


if __name__ == "__main__":
    import config.settings  # noqa: F401  触发统一日志

    logger.info("接口总数：%s", len(get_all_interfaces()))
    logger.info("login 配置：%s", get_interface_config("/login"))
