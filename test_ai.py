from src.core.ai_utils import AIUtils

# 初始化AI工具
ai_utils = AIUtils()

# 测试用例生成
print("=== 生成测试用例 ===")
api_description = "用户登录接口，接收username和password参数，返回token和用户信息"
test_cases = ai_utils.generate_test_cases(api_description)
print("生成的测试用例:", test_cases)

# 安全风险检测
print("\n=== 检测安全风险 ===")
request_data = {
    "username": "admin",
    "password": "1' OR 1=1 --"
}
risks = ai_utils.detect_security_risks(request_data)
print("安全风险检测结果:", risks)
