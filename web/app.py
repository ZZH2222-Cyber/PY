#!/usr/bin/env python
# web/app.py
"""Web应用入口：提供Web界面和API接口"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from config.settings import BASE_URL, DEEPSEEK_API_KEY
from core.request_handler import RequestHandler
from utils.ai_helper import generate_test_cases as ai_generate
from core.api_doc_parser import parse_api_document, standardize_api_metadata
from core.prompt_builder_simple import build_prompt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'


@app.route('/')
def index():
    """首页"""
    return render_template('index.html', base_url=BASE_URL)


@app.route('/api/test', methods=['POST'])
def run_test():
    """运行测试接口"""
    try:
        data = request.json
        base_url = data.get('base_url', BASE_URL)
        endpoint = data.get('endpoint', '')
        method = data.get('method', 'GET')
        headers = data.get('headers', {})
        body = data.get('body', {})
        
        # 确保headers和body是字典类型
        if not isinstance(headers, dict):
            headers = {}
        if not isinstance(body, dict):
            body = {}
        
        # 创建请求处理器
        client = RequestHandler(base_url=base_url)
        
        # 发送请求
        if method == 'GET':
            response = client.get(endpoint, headers=headers)
        elif method == 'POST':
            response = client.post(endpoint, json=body, headers=headers)
        elif method == 'PUT':
            response = client.put(endpoint, json=body, headers=headers)
        elif method == 'DELETE':
            response = client.delete(endpoint, headers=headers)
        else:
            return jsonify({'status': 'error', 'message': '不支持的请求方法'})
        
        # 处理响应
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {'content': response.text}
        
        # 集成现有的断言逻辑
        from core.assertions import ApiAssertions
        
        # 导入安全检测模块
        from testcases.security.run_detector import run_detection
        
        assertions = []
        # 状态码断言
        try:
            ApiAssertions.assert_status_code(response, 200)
            status_passed = True
        except AssertionError:
            status_passed = False
        
        assertions.append({
            'type': 'status_code',
            'expected': 200,
            'actual': response.status_code,
            'passed': status_passed
        })
        
        # 执行安全检测
        import logging
        logger = logging.getLogger(__name__)
        security_results = []
        try:
            target_url = f"{base_url}{endpoint}"
            # 调用安全检测
            security_results = run_detection(target_url)
            logger.info(f"安全检测完成，发现 {len(security_results)} 个安全问题")
        except Exception as e:
            logger.error(f"安全检测失败: {e}")
        
        # 将安全检测结果添加到断言中
        for i, security_issue in enumerate(security_results):
            assertions.append({
                'type': 'security',
                'expected': '无安全漏洞',
                'actual': f"{security_issue.get('type', '未知')}: {security_issue.get('payload', '')}",
                'passed': False
            })
        
        # 生成Allure报告
        import os
        import subprocess
        import tempfile
        import uuid
        import time
        
        allure_report_url = None
        
        try:
            # 创建临时测试目录（不使用with语句，避免自动删除）
            temp_dir = tempfile.mkdtemp()
            try:
                # 直接创建Allure结果目录
                allure_results_dir = os.path.join(temp_dir, 'allure-results')
                os.makedirs(allure_results_dir, exist_ok=True)
                
                # 创建Allure测试结果JSON文件（使用pytest-allure格式）
                test_uuid = str(uuid.uuid4())
                test_result = {
                    "name": f"test_{method.lower()}_{endpoint.replace('/', '_').replace('?', '_').replace('=', '_')}",
                    "fullName": f"api_test#{method.lower()}_{endpoint.replace('/', '_').replace('?', '_').replace('=', '_')}",
                    "status": "passed" if status_passed and len(security_results) == 0 else "failed",
                    "description": "测试通过" if status_passed and len(security_results) == 0 else "测试失败",
                    "start": int(time.time() * 1000),
                    "stop": int((time.time() + 1) * 1000),
                    "uuid": test_uuid,
                    "historyId": str(uuid.uuid4()),
                    "testCaseId": str(uuid.uuid4()),
                    "steps": [
                        {
                            "name": f"发送{method}请求到 {base_url}{endpoint}",
                            "status": "passed" if status_passed else "failed",
                            "start": int(time.time() * 1000),
                            "stop": int((time.time() + 0.5) * 1000),
                            "steps": []
                        }
                    ],
                    "attachments": [],
                    "parameters": [],
                    "labels": [
                        {"name": "feature", "value": "API测试"},
                        {"name": "story", "value": "接口测试"},
                        {"name": "severity", "value": "normal"},
                        {"name": "suite", "value": "api_test"},
                        {"name": "host", "value": "victor"},
                        {"name": "thread", "value": "MainThread"},
                        {"name": "framework", "value": "pytest"},
                        {"name": "language", "value": "cpython3"},
                        {"name": "package", "value": "api_test"}
                    ]
                }
                
                # 添加安全检测步骤
                if security_results:
                    security_step = {
                        "name": "安全检测",
                        "status": "failed",
                        "start": int((time.time() + 0.5) * 1000),
                        "stop": int((time.time() + 1) * 1000),
                        "steps": []
                    }
                    for issue in security_results:
                        security_step["steps"].append({
                            "name": f"{issue.get('type', '未知')}漏洞: {issue.get('payload', '')}",
                            "status": "failed",
                            "start": int((time.time() + 0.6) * 1000),
                            "stop": int((time.time() + 0.9) * 1000),
                            "steps": []
                        })
                    test_result["steps"].append(security_step)
                
                # 写入测试结果文件（文件名格式：{uuid}-result.json）
                result_file = os.path.join(allure_results_dir, f"{test_uuid}-result.json")
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(test_result, f, ensure_ascii=False, indent=2)
                
                logger.info(f"已创建Allure测试结果文件: {result_file}")
                
                # 尝试使用allure命令
                try:
                    # 生成Allure报告
                    logger.info("生成Allure报告")
                    allure_report_dir = os.path.join(temp_dir, 'allure-report')
                    # 使用完整的allure命令路径
                    allure_path = 'D:\\Documents\\allure报告\\allure-2.38.1\\bin\\allure.bat'
                    allure_cmd = [allure_path, 'generate', allure_results_dir, '-o', allure_report_dir, '--clean']
                    
                    logger.info(f"开始运行allure命令: {allure_cmd}")
                    process = subprocess.Popen(allure_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    stdout, stderr = process.communicate(timeout=30)
                    
                    logger.info(f"allure stdout: {stdout}")
                    logger.info(f"allure stderr: {stderr}")
                    
                    if process.returncode != 0:
                        logger.error(f"allure报告生成失败: {stderr}")
                    else:
                        logger.info("Allure报告生成成功")
                        
                        # 复制报告到项目目录，便于访问
                        project_allure_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'allure-report')
                        import shutil
                        try:
                            if os.path.exists(project_allure_dir):
                                shutil.rmtree(project_allure_dir)
                            shutil.copytree(allure_report_dir, project_allure_dir)
                            logger.info(f"Allure报告已复制到: {project_allure_dir}")
                            allure_report_url = 'http://127.0.0.1:5000/allure-report/'
                            logger.info(f"Allure报告地址: {allure_report_url}")
                        except Exception as e:
                            logger.error(f"复制Allure报告失败: {e}")
                            print(f"复制Allure报告失败: {e}")
                            allure_report_url = None
                except Exception as e:
                    logger.warning(f"allure命令不可用，无法生成报告: {e}")
                    print(f"allure命令不可用，无法生成报告: {e}")
            finally:
                # 手动删除临时目录
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info(f"已删除临时目录: {temp_dir}")
        except Exception as e:
            allure_report_url = None
            logger.error(f"生成Allure报告失败: {e}")
            print(f"生成Allure报告失败: {e}")
        
        result = {
            'status': 'success',
            'message': '测试执行成功',
            'response': {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response_data
            },
            'assertions': assertions,
            'security_results': security_results,
            'allure_report_url': allure_report_url
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/ai/generate', methods=['POST'])
def generate_test_cases():
    """AI生成测试用例"""
    try:
        data = request.json
        api_doc = data.get('apiDoc', '')
        
        # 调用AI生成测试用例
        result = ai_generate(api_doc)
        
        return jsonify({
            'status': 'success',
            'message': '测试用例生成成功',
            'business_prompt': result.get('business_prompt', ''),
            'test_cases': result.get('test_cases', [])
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/excel/download', methods=['POST'])
def download_excel():
    """下载Excel测试用例"""
    try:
        data = request.json
        test_cases = data.get('test_cases', [])
        
        if not test_cases:
            return jsonify({'status': 'error', 'message': '测试用例为空'})
        
        # 生成Excel文件路径
        import tempfile
        import os
        from utils.ai_helper import save_to_excel
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # 保存测试用例到Excel
        save_to_excel(test_cases, temp_path)
        
        # 生成Allure报告
        import subprocess
        import logging
        import json
        import uuid
        import time
        
        logger = logging.getLogger(__name__)
        allure_report_url = None
        
        try:
            # 创建临时测试目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 直接创建Allure结果目录
                allure_results_dir = os.path.join(temp_dir, 'allure-results')
                os.makedirs(allure_results_dir, exist_ok=True)
                
                # 为每个测试用例创建Allure测试结果JSON文件
                for i, test_case in enumerate(test_cases):
                    test_result = {
                        "uuid": str(uuid.uuid4()),
                        "historyId": str(uuid.uuid4()),
                        "testCaseName": f"AI生成测试用例 - {test_case.get('name', f'测试用例{i+1}')}",
                        "fullName": f"ai_test.{test_case.get('name', f'test_case_{i+1}').replace(' ', '_')}",
                        "status": "pending",
                        "statusDetails": {
                            "message": "测试用例已生成",
                            "trace": ""
                        },
                        "start": int(time.time() * 1000),
                        "stop": int((time.time() + 1) * 1000),
                        "steps": [],
                        "attachments": [],
                        "parameters": [
                            {"name": "接口路径", "value": test_case.get('endpoint', '')},
                            {"name": "请求方法", "value": test_case.get('method', '')},
                            {"name": "测试类型", "value": test_case.get('type', '')}
                        ],
                        "labels": [
                            {"name": "feature", "value": "AI测试用例"},
                            {"name": "story", "value": "测试用例生成"},
                            {"name": "severity", "value": "normal"}
                        ]
                    }
                    
                    # 写入测试结果文件
                    result_file = os.path.join(allure_results_dir, f"result-{test_result['uuid']}.json")
                    with open(result_file, 'w', encoding='utf-8') as f:
                        json.dump(test_result, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"已创建Allure测试结果文件: {result_file}")
                
                # 尝试使用allure命令
                try:
                    # 生成Allure报告
                    logger.info("生成Allure报告")
                    allure_report_dir = os.path.join(temp_dir, 'allure-report')
                    # 使用完整的allure命令路径
                    allure_path = 'D:\\Documents\\allure报告\\allure-2.38.1\\bin\\allure.bat'
                    allure_cmd = [allure_path, 'generate', allure_results_dir, '-o', allure_report_dir, '--clean']
                    
                    logger.info(f"开始运行allure命令: {allure_cmd}")
                    process = subprocess.Popen(allure_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    stdout, stderr = process.communicate(timeout=30)
                    
                    logger.info(f"allure stdout: {stdout}")
                    logger.info(f"allure stderr: {stderr}")
                    
                    if process.returncode != 0:
                        logger.error(f"allure报告生成失败: {stderr}")
                    else:
                        logger.info("Allure报告生成成功")
                        
                        # 复制报告到项目目录，便于访问
                        project_allure_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'allure-report')
                        import shutil
                        try:
                            if os.path.exists(project_allure_dir):
                                shutil.rmtree(project_allure_dir)
                            shutil.copytree(allure_report_dir, project_allure_dir)
                            logger.info(f"Allure报告已复制到: {project_allure_dir}")
                            allure_report_url = 'http://127.0.0.1:5000/allure-report/'
                            logger.info(f"Allure报告地址: {allure_report_url}")
                        except Exception as e:
                            logger.error(f"复制Allure报告失败: {e}")
                            allure_report_url = None
                except Exception as e:
                    logger.warning(f"allure命令不可用，无法生成报告: {e}")
        except Exception as e:
            allure_report_url = None
            logger.error(f"生成Allure报告失败: {e}")
            print(f"生成Allure报告失败: {e}")
        
        # 返回文件下载和Allure报告地址
        response = send_file(temp_path, as_attachment=True, download_name='test_cases.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # 在响应中添加Allure报告地址
        response.headers['X-Allure-Report-Url'] = allure_report_url
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/error/analyze', methods=['POST'])
def analyze_error():
    """分析错误"""
    try:
        data = request.json
        test_case = data.get('test_case', {})
        response_data = data.get('response', {})
        
        # 创建模拟响应对象
        class MockResponse:
            def __init__(self, status_code, headers, data):
                self.status_code = status_code
                self.headers = headers
                self._data = data
            
            def json(self):
                return self._data
            
            @property
            def text(self):
                return str(self._data)
        
        # 提取响应信息
        status_code = response_data.get('status_code', 500)
        headers = response_data.get('headers', {})
        response_body = response_data.get('data', {})
        
        # 创建模拟响应对象
        mock_response = MockResponse(status_code, headers, response_body)
        
        # 分析错误
        from utils.error_analyzer import ErrorAnalyzer
        analysis = ErrorAnalyzer.analyze_test_failure(test_case, mock_response)
        
        return jsonify({
            'status': 'success',
            'message': '错误分析完成',
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/simple/generate', methods=['POST'])
def generate_simple_test():
    """简便测试 - 生成测试用例"""
    try:
        # 获取接口地址
        api_url = request.form.get('api_url')
        if not api_url:
            return jsonify({'status': 'error', 'message': '请输入接口地址'})
        
        # 获取API文档
        api_doc_file = request.files.get('api_doc_file')
        api_doc_text = request.form.get('api_doc_text')
        
        if not api_doc_file and not api_doc_text:
            return jsonify({'status': 'error', 'message': '请上传API文档或粘贴文档内容'})
        
        # 读取文档内容
        content = None
        if api_doc_file:
            # 读取文件内容
            content = api_doc_file.read().decode('utf-8')
            # 确定文件类型
            filename = api_doc_file.filename
            if filename.endswith('.json'):
                # 尝试判断是OpenAPI还是Postman
                try:
                    data = json.loads(content)
                    if 'swagger' in data or 'openapi' in data:
                        file_type = 'openapi'
                    elif 'info' in data and 'item' in data:
                        file_type = 'postman'
                    else:
                        file_type = 'text'
                except:
                    file_type = 'text'
            elif filename.endswith('.yaml') or filename.endswith('.yml'):
                file_type = 'openapi'
            else:
                file_type = 'text'
        else:
            content = api_doc_text
            file_type = 'text'
        
        # 解析文档
        parsed_info = parse_api_document(content, file_type)
        
        # 标准化API元数据
        api_metadata = standardize_api_metadata(api_url, parsed_info)
        
        # 构建提示词
        prompt = build_prompt(api_metadata)
        
        # 调用AI生成测试用例
        from utils.ai_helper import generate_test_cases
        result = generate_test_cases(prompt)
        
        # 处理生成的测试用例
        test_cases = result.get('test_cases', [])
        
        # 如果没有生成测试用例，返回模拟数据
        if not test_cases:
            # 生成模拟测试用例
            test_cases = [
                {
                    "name": "正常请求",
                    "method": api_metadata.get('method', 'GET'),
                    "path": api_metadata.get('url', '/'),
                    "headers": {"Content-Type": "application/json"},
                    "body": {},
                    "expected_status": 200
                },
                {
                    "name": "缺少必填字段",
                    "method": api_metadata.get('method', 'GET'),
                    "path": api_metadata.get('url', '/'),
                    "headers": {"Content-Type": "application/json"},
                    "body": {},
                    "expected_status": 400
                },
                {
                    "name": "SQL注入尝试",
                    "method": api_metadata.get('method', 'GET'),
                    "path": api_metadata.get('url', '/'),
                    "headers": {"Content-Type": "application/json"},
                    "body": {"name": "' OR '1'='1"},
                    "expected_status": 400
                }
            ]
        
        return jsonify({
            'status': 'success',
            'message': '测试用例生成成功',
            'test_cases': test_cases
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})





@app.route('/allure-report/<path:path>')
def serve_allure_report(path):
    """提供Allure报告的静态文件访问"""
    import os
    allure_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'allure-report')
    return send_from_directory(allure_dir, path)


@app.route('/allure-report/')
def serve_allure_report_index():
    """提供Allure报告的首页访问"""
    import os
    allure_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'allure-report')
    return send_from_directory(allure_dir, 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)