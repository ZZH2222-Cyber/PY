from src.utils.excel_utils import read_excel
from src.core.request_handler import RequestHandler

# 读取测试数据
test_data = read_excel('data/test_data.xlsx', 'Login')
print("=== 读取的测试数据 ===")
for test_case in test_data:
    print(test_case)

# 模拟登录测试
handler = RequestHandler()
print("\n=== 执行登录测试 ===")
for test_case in test_data:
    print(f"\n执行测试用例: {test_case['TestCase']}")
    print(f"用户名: {test_case['Username']}, 密码: {test_case['Password']}")
    print(f"预期结果: {test_case['ExpectedResult']}")
    
    # 模拟登录请求
    response = handler.request('POST', 'https://jsonplaceholder.typicode.com/posts', 
                              json={"username": test_case['Username'], "password": test_case['Password']})
    print(f"实际响应状态码: {response.status_code}")
