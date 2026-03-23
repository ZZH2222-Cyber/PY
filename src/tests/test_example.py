import pytest
from src.core.request_handler import RequestHandler
from src.core.assertion import Assertion
from src.utils.excel_utils import read_excel

@pytest.fixture(scope='session')
def request_handler():
    """
    请求处理器fixture
    """
    handler = RequestHandler()
    yield handler
    handler.close()

@pytest.fixture(scope='module')
def test_data():
    """
    测试数据fixture
    """
    return read_excel('data/test_data.xlsx')

class TestExample:
    """
    示例测试类
    """
    
    def test_get_example(self, request_handler):
        """
        测试GET请求
        """
        url = "https://jsonplaceholder.typicode.com/posts/1"
        response = request_handler.get(url)
        
        # 断言状态码
        Assertion.assert_status_code(response, 200)
        
        # 断言响应时间
        Assertion.assert_response_time(response, 5)
        
        # 断言JSON字段
        Assertion.assert_json_field(response, "userId", 1)
        Assertion.assert_json_field(response, "id", 1)
    
    def test_post_example(self, request_handler):
        """
        测试POST请求
        """
        url = "https://jsonplaceholder.typicode.com/posts"
        data = {
            "title": "测试标题",
            "body": "测试内容",
            "userId": 1
        }
        response = request_handler.post(url, json=data)
        
        # 断言状态码
        Assertion.assert_status_code(response, 201)
        
        # 断言响应时间
        Assertion.assert_response_time(response, 5)
        
        # 断言JSON字段
        Assertion.assert_json_field(response, "title", "测试标题")
        Assertion.assert_json_field(response, "body", "测试内容")
        Assertion.assert_json_field(response, "userId", 1)
    
    def test_data_driven(self, request_handler, test_data):
        """
        数据驱动测试
        """
        for item in test_data:
            print(f"测试数据: {item}")
            # 这里可以使用测试数据进行测试
            assert item["ID"] is not None
            assert item["Name"] is not None
