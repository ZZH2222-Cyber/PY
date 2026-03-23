import jsonschema
import time

class Assertion:
    """
    断言库，用于验证接口响应
    """
    
    @staticmethod
    def assert_status_code(response, expected_status_code):
        """
        断言响应状态码
        
        Args:
            response: 响应对象
            expected_status_code: 期望的状态码
        
        Raises:
            AssertionError: 如果状态码不匹配
        """
        assert response.status_code == expected_status_code, \
            f"状态码不匹配，期望: {expected_status_code}，实际: {response.status_code}"
    
    @staticmethod
    def assert_json_field(response, field_path, expected_value):
        """
        断言JSON响应中的字段值
        
        Args:
            response: 响应对象
            field_path: 字段路径，如 "data.user.name"
            expected_value: 期望的字段值
        
        Raises:
            AssertionError: 如果字段值不匹配
        """
        try:
            json_data = response.json()
            # 解析字段路径
            fields = field_path.split('.')
            value = json_data
            for field in fields:
                value = value[field]
            assert value == expected_value, \
                f"字段值不匹配，字段: {field_path}，期望: {expected_value}，实际: {value}"
        except (ValueError, KeyError) as e:
            raise AssertionError(f"无法获取字段 {field_path}: {str(e)}")
    
    @staticmethod
    def assert_response_time(response, max_time):
        """
        断言响应时间
        
        Args:
            response: 响应对象
            max_time: 最大响应时间（秒）
        
        Raises:
            AssertionError: 如果响应时间超过最大值
        """
        if hasattr(response, 'elapsed'):
            elapsed_time = response.elapsed.total_seconds()
            assert elapsed_time <= max_time, \
                f"响应时间过长，期望: {max_time}s，实际: {elapsed_time:.2f}s"
        else:
            raise AssertionError("响应对象没有elapsed属性")
    
    @staticmethod
    def assert_json_schema(response, schema):
        """
        断言JSON响应符合Schema
        
        Args:
            response: 响应对象
            schema: JSON Schema
        
        Raises:
            AssertionError: 如果JSON不符合Schema
        """
        try:
            json_data = response.json()
            jsonschema.validate(instance=json_data, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            raise AssertionError(f"JSON Schema验证失败: {str(e)}")
        except ValueError as e:
            raise AssertionError(f"无法解析JSON响应: {str(e)}")
    
    @staticmethod
    def assert_response_contains(response, expected_content):
        """
        断言响应内容包含指定字符串
        
        Args:
            response: 响应对象
            expected_content: 期望包含的字符串
        
        Raises:
            AssertionError: 如果响应内容不包含指定字符串
        """
        content = response.text
        assert expected_content in content, \
            f"响应内容不包含期望字符串: {expected_content}"
