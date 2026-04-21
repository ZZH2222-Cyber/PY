# core/api_doc_parser.py
"""API文档解析器：支持OpenAPI、Postman和纯文本格式"""

import json
import re
from typing import Dict, Any, List


def parse_api_document(content: str, file_type: str) -> Dict[str, Any]:
    """解析API文档，提取接口信息
    
    参数:
        content: 文档内容
        file_type: 文档类型，可选值: 'openapi', 'postman', 'text'
    
    返回:
        包含接口信息的字典
    """
    if file_type == 'openapi':
        return _parse_openapi(content)
    elif file_type == 'postman':
        return _parse_postman(content)
    else:  # text
        return _parse_text(content)


def _parse_openapi(content: str) -> Dict[str, Any]:
    """解析OpenAPI文档"""
    try:
        spec = json.loads(content)
        paths = spec.get('paths', {})
        
        # 提取第一个路径（假设用户只关注一个接口）
        for path, methods in paths.items():
            for method, details in methods.items():
                return {
                    'method': method.upper(),
                    'path': path,
                    'params': _extract_openapi_params(details),
                    'description': details.get('description', '')
                }
        
        # 如果没有找到路径，返回默认值
        return {
            'method': 'GET',
            'path': '/',
            'params': [],
            'description': 'OpenAPI文档中未找到路径信息'
        }
    except Exception as e:
        # 解析失败，返回默认值
        return {
            'method': 'GET',
            'path': '/',
            'params': [],
            'description': f'OpenAPI解析失败: {str(e)}'
        }


def _extract_openapi_params(details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """从OpenAPI详情中提取参数"""
    params = []
    
    # 提取路径参数
    if 'parameters' in details:
        for param in details['parameters']:
            params.append({
                'name': param.get('name', ''),
                'in': param.get('in', 'query'),
                'type': param.get('schema', {}).get('type', 'string'),
                'required': param.get('required', False),
                'constraints': _extract_constraints(param.get('schema', {})),
                'description': param.get('description', '')
            })
    
    # 提取请求体参数
    if 'requestBody' in details:
        request_body = details['requestBody']
        if 'content' in request_body:
            for content_type, content_details in request_body['content'].items():
                if 'application/json' in content_type:
                    schema = content_details.get('schema', {})
                    if 'properties' in schema:
                        for prop_name, prop_details in schema['properties'].items():
                            params.append({
                                'name': prop_name,
                                'in': 'body',
                                'type': prop_details.get('type', 'string'),
                                'required': prop_name in schema.get('required', []),
                                'constraints': _extract_constraints(prop_details),
                                'description': prop_details.get('description', '')
                            })
    
    return params


def _extract_constraints(schema: Dict[str, Any]) -> str:
    """从schema中提取约束条件"""
    constraints = []
    
    if 'minLength' in schema:
        constraints.append(f'minLength {schema["minLength"]}')
    if 'maxLength' in schema:
        constraints.append(f'maxLength {schema["maxLength"]}')
    if 'minimum' in schema:
        constraints.append(f'minimum {schema["minimum"]}')
    if 'maximum' in schema:
        constraints.append(f'maximum {schema["maximum"]}')
    if 'enum' in schema:
        constraints.append(f'enum {schema["enum"]}')
    
    return ', '.join(constraints)


def _parse_postman(content: str) -> Dict[str, Any]:
    """解析Postman Collection"""
    try:
        collection = json.loads(content)
        
        # 取第一个请求
        if 'item' in collection and collection['item']:
            first_item = collection['item'][0]
            if 'request' in first_item:
                req = first_item['request']
                return {
                    'method': req.get('method', 'GET'),
                    'path': _extract_postman_url(req.get('url', {})),
                    'params': _extract_postman_params(req),
                    'description': first_item.get('name', '')
                }
        
        # 如果没有找到请求，返回默认值
        return {
            'method': 'GET',
            'path': '/',
            'params': [],
            'description': 'Postman Collection中未找到请求信息'
        }
    except Exception as e:
        # 解析失败，返回默认值
        return {
            'method': 'GET',
            'path': '/',
            'params': [],
            'description': f'Postman解析失败: {str(e)}'
        }


def _extract_postman_url(url: Dict[str, Any]) -> str:
    """从Postman URL中提取路径"""
    if isinstance(url, str):
        # 如果是字符串，直接返回
        return url
    elif 'raw' in url:
        # 如果有raw字段，返回raw
        return url['raw']
    elif 'path' in url:
        # 如果有path字段，拼接路径
        path_parts = url['path']
        if isinstance(path_parts, list):
            return '/' + '/'.join(path_parts)
        else:
            return path_parts
    else:
        return '/'


def _extract_postman_params(req: Dict[str, Any]) -> List[Dict[str, Any]]:
    """从Postman请求中提取参数"""
    params = []
    
    # 提取查询参数
    if 'url' in req and 'query' in req['url']:
        for param in req['url']['query']:
            params.append({
                'name': param.get('key', ''),
                'in': 'query',
                'type': 'string',
                'required': param.get('value', '') != '',
                'constraints': '',
                'description': param.get('description', '')
            })
    
    # 提取请求体参数
    if 'body' in req:
        body = req['body']
        if body.get('mode') == 'raw':
            try:
                body_json = json.loads(body.get('raw', '{}'))
                for key, value in body_json.items():
                    params.append({
                        'name': key,
                        'in': 'body',
                        'type': type(value).__name__,
                        'required': True,
                        'constraints': '',
                        'description': ''
                    })
            except:
                pass
    
    return params


def _parse_text(content: str) -> Dict[str, Any]:
    """解析纯文本/Markdown文档"""
    # 尝试从文本中提取接口信息
    method = _extract_method(content)
    path = _extract_path(content)
    params = _extract_text_params(content)
    description = _extract_description(content)
    
    return {
        'method': method,
        'path': path,
        'params': params,
        'description': description
    }


def _extract_method(content: str) -> str:
    """从文本中提取HTTP方法"""
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
    for method in methods:
        if re.search(rf'\b{method}\b', content, re.IGNORECASE):
            return method
    return 'GET'


def _extract_path(content: str) -> str:
    """从文本中提取路径"""
    # 尝试匹配路径格式
    path_patterns = [
        r'path\s*[:=]\s*["\']([^"\']+)["\']',
        r'endpoint\s*[:=]\s*["\']([^"\']+)["\']',
        r'url\s*[:=]\s*["\']([^"\']+)["\']',
        r'\b(/[\w\-/]+)\b'
    ]
    
    for pattern in path_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return '/'


def _extract_text_params(content: str) -> List[Dict[str, Any]]:
    """从文本中提取参数"""
    params = []
    
    # 尝试匹配参数格式
    param_patterns = [
        r'param\s+([\w]+)\s*[:=]\s*([^\n]+)',
        r'([\w]+)\s*[:=]\s*([^\n]+)',
        r'\b([\w]+)\b.*?\btype\b.*?([\w]+)'
    ]
    
    for pattern in param_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if len(match.groups()) >= 1:
                param_name = match.group(1)
                param_type = 'string'
                if len(match.groups()) >= 2:
                    param_type = match.group(2).strip()
                
                params.append({
                    'name': param_name,
                    'in': 'body',
                    'type': param_type,
                    'required': True,
                    'constraints': '',
                    'description': ''
                })
    
    return params


def _extract_description(content: str) -> str:
    """从文本中提取描述"""
    # 尝试提取第一行作为描述
    lines = content.strip().split('\n')
    if lines:
        return lines[0].strip()
    return '接口描述'


def standardize_api_metadata(api_url: str, parsed_info: Dict[str, Any]) -> Dict[str, Any]:
    """标准化API元数据
    
    参数:
        api_url: 用户输入的完整接口地址
        parsed_info: 解析后的接口信息
    
    返回:
        标准化的API元数据
    """
    # 解析完整URL
    from urllib.parse import urlparse
    parsed_url = urlparse(api_url)
    
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    path = parsed_info.get('path', parsed_url.path)
    
    # 如果path是完整URL，提取路径部分
    if '://' in path:
        path_parsed = urlparse(path)
        path = path_parsed.path
    
    # 确保path以/开头
    if not path.startswith('/'):
        path = '/' + path
    
    return {
        'method': parsed_info.get('method', 'GET'),
        'url': path,
        'base_url': base_url,
        'params': parsed_info.get('params', []),
        'description': parsed_info.get('description', '接口描述')
    }
