from src.core.request_handler import RequestHandler
from src.core.assertion import Assertion

# 初始化请求处理器
handler = RequestHandler()

# 发送请求
response = handler.request('GET', 'https://jsonplaceholder.typicode.com/posts/1')

# 执行断言
print("=== 执行状态码断言 ===")
Assertion.assert_status_code(response, 200)
print("状态码断言通过")

print("\n=== 执行JSON字段断言 ===")
Assertion.assert_json_field(response, 'id', 1)
print("JSON字段断言通过")

print("\n=== 执行响应时间断言 ===")
Assertion.assert_response_time(response, 3)  # 3秒内
print("响应时间断言通过")
