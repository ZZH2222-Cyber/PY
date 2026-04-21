#!/usr/bin/env python
# utils/error_analyzer.py
"""错误分析和源头查询工具"""

import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ErrorAnalyzer:
    """错误分析器"""
    
    @staticmethod
    def analyze_error(response: Any, expected_status: int = 200) -> Dict[str, Any]:
        """分析错误响应
        
        参数:
            response: 响应对象
            expected_status: 期望的状态码
            
        返回:
            错误分析结果
        """
        analysis = {
            'status': 'error',
            'actual_status': response.status_code,
            'expected_status': expected_status,
            'error_type': '',
            'error_message': '',
            'possible_causes': [],
            'suggestions': []
        }
        
        # 分析状态码
        if response.status_code == 400:
            analysis['error_type'] = 'Bad Request'
            analysis['error_message'] = '请求参数错误'
            analysis['possible_causes'] = [
                '请求参数格式错误',
                '缺少必填参数',
                '参数值不符合要求'
            ]
            analysis['suggestions'] = [
                '检查请求参数格式',
                '确保所有必填参数都已提供',
                '验证参数值是否符合要求'
            ]
        elif response.status_code == 401:
            analysis['error_type'] = 'Unauthorized'
            analysis['error_message'] = '未授权访问'
            analysis['possible_causes'] = [
                '缺少认证信息',
                '认证信息无效',
                '认证已过期'
            ]
            analysis['suggestions'] = [
                '检查是否提供了正确的认证信息',
                '验证认证令牌是否有效',
                '重新获取认证令牌'
            ]
        elif response.status_code == 403:
            analysis['error_type'] = 'Forbidden'
            analysis['error_message'] = '禁止访问'
            analysis['possible_causes'] = [
                '没有足够的权限',
                '访问被拒绝'
            ]
            analysis['suggestions'] = [
                '检查用户权限',
                '确保用户有访问该资源的权限'
            ]
        elif response.status_code == 404:
            analysis['error_type'] = 'Not Found'
            analysis['error_message'] = '资源不存在'
            analysis['possible_causes'] = [
                '接口路径错误',
                '资源ID不存在',
                'API版本错误'
            ]
            analysis['suggestions'] = [
                '检查接口路径是否正确',
                '验证资源ID是否存在',
                '确认API版本是否正确'
            ]
        elif response.status_code == 500:
            analysis['error_type'] = 'Internal Server Error'
            analysis['error_message'] = '服务器内部错误'
            analysis['possible_causes'] = [
                '服务器代码错误',
                '数据库连接失败',
                '服务器资源不足'
            ]
            analysis['suggestions'] = [
                '联系后端开发人员',
                '检查服务器日志',
                '稍后重试'
            ]
        else:
            analysis['error_type'] = 'Unknown Error'
            analysis['error_message'] = f'未知错误 (状态码: {response.status_code})'
            analysis['possible_causes'] = ['未知原因']
            analysis['suggestions'] = ['检查请求和服务器状态']
        
        # 尝试解析响应体获取更多错误信息
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                if 'error' in error_data:
                    analysis['error_message'] = error_data['error']
                elif 'message' in error_data:
                    analysis['error_message'] = error_data['message']
        except json.JSONDecodeError:
            pass
        
        return analysis
    
    @staticmethod
    def analyze_test_failure(test_case: Dict[str, Any], response: Any) -> Dict[str, Any]:
        """分析测试失败原因
        
        参数:
            test_case: 测试用例
            response: 响应对象
            
        返回:
            失败分析结果
        """
        expected_status = test_case.get('expected_status', 200)
        analysis = ErrorAnalyzer.analyze_error(response, expected_status)
        
        # 添加测试用例信息
        analysis['test_case'] = {
            'title': test_case.get('title', ''),
            'method': test_case.get('method', ''),
            'path': test_case.get('path', ''),
            'body': test_case.get('body', {})
        }
        
        # 添加响应信息
        try:
            analysis['response'] = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response.json()
            }
        except json.JSONDecodeError:
            analysis['response'] = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response.text
            }
        
        return analysis
    
    @staticmethod
    def generate_error_report(failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成错误报告
        
        参数:
            failures: 失败分析结果列表
            
        返回:
            错误报告
        """
        report = {
            'total_failures': len(failures),
            'error_types': {},
            'status_codes': {},
            'failures': failures
        }
        
        # 统计错误类型和状态码
        for failure in failures:
            error_type = failure.get('error_type', 'Unknown')
            status_code = failure.get('actual_status', 0)
            
            # 统计错误类型
            if error_type in report['error_types']:
                report['error_types'][error_type] += 1
            else:
                report['error_types'][error_type] = 1
            
            # 统计状态码
            status_code_str = str(status_code)
            if status_code_str in report['status_codes']:
                report['status_codes'][status_code_str] += 1
            else:
                report['status_codes'][status_code_str] = 1
        
        return report