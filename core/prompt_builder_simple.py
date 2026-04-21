# core/prompt_builder_simple.py
"""提示词构建器：生成AI测试用例提示词"""

import json
from pathlib import Path


def build_prompt(api_metadata: Dict[str, Any]) -> str:
    """构建AI提示词
    
    参数:
        api_metadata: 标准化的API元数据
    
    返回:
        完整的提示词
    """
    # 加载基础提示词模板
    base_prompt = _load_base_prompt()
    
    # 将API元数据转换为JSON字符串
    api_metadata_json = json.dumps(api_metadata, ensure_ascii=False, indent=2)
    
    # 替换模板中的占位符
    prompt = base_prompt.replace('{api_metadata_json}', api_metadata_json)
    
    return prompt


def _load_base_prompt() -> str:
    """加载基础提示词模板"""
    # 尝试从文件加载模板
    template_path = Path(__file__).parent.parent / 'prompts' / 'base.txt'
    
    if template_path.exists():
        return template_path.read_text(encoding='utf-8')
    else:
        # 如果文件不存在，返回默认模板
        return """
你是一位资深测试工程师。请根据以下接口信息生成测试用例。

要求必须覆盖：
- 正常场景：至少1条
- 边界场景：空值、超长、最小值、最大值、负数、零（如适用）
- 异常场景：参数类型错误、缺失必填字段、不存在的资源ID
- 安全场景：SQL注入（如 ' OR '1'='1）、XSS（<script>alert(1)</script>）、路径遍历（../../etc/passwd）

输出格式：JSON数组，每个元素包含：
{
  "name": "用例描述",
  "method": "HTTP方法",
  "path": "接口路径",
  "headers": {"Content-Type": "application/json"},
  "body": {参数名: 值},
  "expected_status": 200
}

接口信息如下（JSON）：
{api_metadata_json}
"""


# 类型提示
from typing import Dict, Any
