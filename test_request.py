from src.core.request_handler import RequestHandler

# 初始化请求处理器
handler = RequestHandler()

# 发送GET请求
print("=== 发送GET请求 ===")
response = handler.request('GET', 'https://jsonplaceholder.typicode.com/posts/1')
print("GET请求响应状态码:", response.status_code)
print("GET请求响应内容:", response.json())

# 发送POST请求
print("\n=== 发送POST请求 ===")
post_data = {
    "title": "测试标题",
    "body": "测试内容",
    "userId": 1
}
response = handler.request('POST', 'https://jsonplaceholder.typicode.com/posts', json=post_data)
print("POST请求响应状态码:", response.status_code)
print("POST请求响应内容:", response.json())
