import requests
import json
import re

class AIUtils:
    """
    AI工具类，提供AI辅助测试功能
    """
    
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        """
        初始化AI工具
        
        Args:
            api_key: API密钥
            model: 使用的模型
        """
        self.api_key = api_key
        self.model = model
    
    def generate_test_cases(self, api_description):
        """
        根据接口描述生成测试用例
        
        Args:
            api_description: 接口描述
        
        Returns:
            list: 生成的测试用例列表
        """
        if not self.api_key:
            # 模拟生成测试用例
            return self._mock_generate_test_cases(api_description)
        
        # 实际调用大模型API
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的接口测试工程师，根据接口描述生成测试用例，包括正常场景、边界值和异常场景"
                    },
                    {
                        "role": "user",
                        "content": f"根据以下接口描述生成测试用例：\n{api_description}"
                    }
                ],
                "temperature": 0.7
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return self._parse_test_cases(result["choices"][0]["message"]["content"])
        except Exception as e:
            print(f"生成测试用例失败: {str(e)}")
            # 失败时返回模拟数据
            return self._mock_generate_test_cases(api_description)
    
    def _mock_generate_test_cases(self, api_description):
        """
        模拟生成测试用例
        
        Args:
            api_description: 接口描述
        
        Returns:
            list: 生成的测试用例列表
        """
        return [
            {
                "case_name": "正常场景测试",
                "method": "GET",
                "url": "/api/test",
                "params": {"id": 1},
                "expected_status": 200,
                "expected_response": {"id": 1, "name": "test"}
            },
            {
                "case_name": "边界值测试",
                "method": "GET",
                "url": "/api/test",
                "params": {"id": 0},
                "expected_status": 400,
                "expected_response": {"error": "Invalid ID"}
            },
            {
                "case_name": "异常场景测试",
                "method": "GET",
                "url": "/api/test",
                "params": {"id": "string"},
                "expected_status": 400,
                "expected_response": {"error": "Invalid ID format"}
            }
        ]
    
    def _parse_test_cases(self, content):
        """
        解析大模型返回的测试用例
        
        Args:
            content: 大模型返回的内容
        
        Returns:
            list: 解析后的测试用例列表
        """
        # 简单解析，实际项目中可以根据返回格式进行更复杂的解析
        test_cases = []
        # 这里只是示例，实际需要根据大模型的返回格式进行调整
        test_cases.append({
            "case_name": "正常场景测试",
            "method": "GET",
            "url": "/api/test",
            "params": {"id": 1},
            "expected_status": 200,
            "expected_response": {"id": 1, "name": "test"}
        })
        return test_cases
    
    def detect_security_risks(self, request_data):
        """
        检测请求数据中的安全风险
        
        Args:
            request_data: 请求数据
        
        Returns:
            dict: 安全风险检测结果
        """
        risks = {
            "sql_injection": self._detect_sql_injection(request_data),
            "prompt_injection": self._detect_prompt_injection(request_data)
        }
        return risks
    
    def _detect_sql_injection(self, request_data):
        """
        检测SQL注入风险
        
        Args:
            request_data: 请求数据
        
        Returns:
            bool: 是否存在SQL注入风险
        """
        # SQL注入检测规则
        sql_patterns = [
            r"'\s*OR\s*1=1",
            r"'\s*AND\s*1=1",
            r"UNION\s+SELECT",
            r"DROP\s+TABLE",
            r"DELETE\s+FROM",
            r"INSERT\s+INTO",
            r"UPDATE\s+.*\s+SET",
            r"--",
            r";\s*DROP",
            r";\s*DELETE",
            r";\s*INSERT",
            r";\s*UPDATE"
        ]
        
        data_str = json.dumps(request_data, ensure_ascii=False)
        for pattern in sql_patterns:
            if re.search(pattern, data_str, re.IGNORECASE):
                return True
        return False
    
    def _detect_prompt_injection(self, request_data):
        """
        检测提示词注入风险
        
        Args:
            request_data: 请求数据
        
        Returns:
            bool: 是否存在提示词注入风险
        """
        # 提示词注入检测规则
        prompt_patterns = [
            r"Ignore previous instructions",
            r"Ignore all previous prompts",
            r"Forget all previous instructions",
            r"Override previous instructions",
            r"Disregard previous instructions",
            r"Bypass security",
            r"Bypass content filter",
            r"Tell me how to hack",
            r"How to bypass",
            r"Ignore content policy"
        ]
        
        data_str = json.dumps(request_data, ensure_ascii=False)
        for pattern in prompt_patterns:
            if re.search(pattern, data_str, re.IGNORECASE):
                return True
        return False
