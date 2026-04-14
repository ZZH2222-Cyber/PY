# utils/ai_helper.py
"""调用 DeepSeek Chat API 生成接口测试用例；无密钥时返回内置示例数据。"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

import requests
from requests.exceptions import RequestException

from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_API_URL

logger = logging.getLogger(__name__)


def _mock_cases(api_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """根据接口摘要生成离线示例用例（不调用外网）。

    参数:
        api_info: 至少可包含 method、path、description 等键。

    返回:
        用例字典列表。

    异常:
        无。
    """
    path = str(api_info.get("path", "/api/demo"))
    method = str(api_info.get("method", "POST")).upper()
    logger.info("使用内置模拟用例，path=%s method=%s", path, method)
    return [
        {
            "title": "正常请求",
            "method": method,
            "path": path,
            "headers": {"Content-Type": "application/json"},
            "body": {"id": 1, "name": "正常数据"},
            "expected_status": 200,
            "category": "positive",
        },
        {
            "title": "缺少必填字段",
            "method": method,
            "path": path,
            "headers": {"Content-Type": "application/json"},
            "body": {},
            "expected_status": 400,
            "category": "negative",
        },
        {
            "title": "边界-超长字符串",
            "method": method,
            "path": path,
            "headers": {"Content-Type": "application/json"},
            "body": {"name": "x" * 5000},
            "expected_status": 400,
            "category": "boundary",
        },
        {
            "title": "安全-SQL注入尝试",
            "method": method,
            "path": path,
            "headers": {"Content-Type": "application/json"},
            "body": {"name": "' OR 1=1 --"},
            "expected_status": 400,
            "category": "security",
        },
    ]


def _parse_json_array_from_content(content: str) -> List[Dict[str, Any]]:
    """从模型返回文本中提取 JSON 数组。

    参数:
        content: 模型原始文本。

    返回:
        字典列表。

    异常:
        ValueError: 无法解析为列表时抛出。
    """
    text = content.strip()
    # 尝试去掉 ```json 围栏
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()

    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("模型返回不是 JSON 数组")
    out: List[Dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict):
            out.append(item)
    if not out:
        raise ValueError("JSON 数组中无有效对象")
    return out


def generate_test_cases_by_ai(api_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """根据接口描述调用 DeepSeek 生成用例（正常/边界/异常/安全）。

    未配置 DEEPSEEK_API_KEY 时返回 _mock_cases，便于离线开发与 CI。

    参数:
        api_info: 接口元数据，如 name、method、path、参数说明、鉴权方式等。

    返回:
        用例列表，每条为 dict（字段名由模型决定，常见含 title、method、path 等）。

    异常:
        requests.RequestException: HTTP 调用失败（记录后抛出）。
        ValueError: 响应无法解析为用例列表。
    """
    if not DEEPSEEK_API_KEY:
        logger.info("未配置 DEEPSEEK_API_KEY，返回模拟用例")
        return _mock_cases(api_info)

    system_prompt = (
        "你是资深测试工程师。根据给定的接口信息，输出**仅包含**一个 JSON 数组，"
        "数组元素为对象，覆盖：正常、边界、异常、安全（含 SQL 注入/XSS payload 思路）。"
        "每个对象建议包含：title, method, path, headers, body, expected_status, category。"
        "不要输出 Markdown 说明，只输出 JSON。"
    )
    user_prompt = json.dumps(api_info, ensure_ascii=False, indent=2)

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    logger.info("调用 DeepSeek 生成用例…")
    try:
        resp = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
    except RequestException as exc:
        logger.error("DeepSeek 请求失败：%s", exc, exc_info=True)
        raise

    try:
        body = resp.json()
        content = body["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError) as exc:
        logger.error("DeepSeek 响应结构异常：%s", exc)
        raise ValueError("无法解析 DeepSeek 响应") from exc

    try:
        cases = _parse_json_array_from_content(content)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("解析模型 JSON 失败：%s 原始片段=%s", exc, content[:500])
        raise ValueError("模型输出不是合法 JSON 数组") from exc

    logger.info("DeepSeek 生成用例 %d 条", len(cases))
    return cases


def save_to_excel(cases: List[Dict[str, Any]], file_path: str) -> None:
    """将用例列表写入 Excel（列为各 dict 的并集）。

    参数:
        cases: 用例字典列表。
        file_path: 输出 .xlsx 路径。

    返回:
        无。

    异常:
        OSError: 无法创建目录或写入文件。
        ValueError: cases 为空。
    """
    if not cases:
        logger.error("save_to_excel: cases 为空")
        raise ValueError("cases 不能为空")

    from openpyxl import Workbook

    logger.info("写入 Excel：%s 共 %d 条", file_path, len(cases))

    keys: List[str] = []
    seen = set()
    for c in cases:
        for k in c.keys():
            if k not in seen:
                seen.add(k)
                keys.append(str(k))

    wb = Workbook()
    ws = wb.active
    ws.title = "ai_cases"
    ws.append(keys)

    def _cell_value(value: Any) -> Any:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return value

    for case in cases:
        ws.append([_cell_value(case.get(k, "")) for k in keys])

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(path))
    logger.info("Excel 已保存：%s", path)