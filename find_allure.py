import os
import subprocess

# 查找allure命令的路径
def find_allure():
    # 尝试在系统路径中查找
    paths = os.environ['PATH'].split(os.pathsep)
    for path in paths:
        allure_path = os.path.join(path, 'allure.bat')
        if os.path.exists(allure_path):
            return allure_path
        allure_path = os.path.join(path, 'allure')
        if os.path.exists(allure_path):
            return allure_path
    return None

# 测试查找结果
allure_path = find_allure()
print(f"Allure路径: {allure_path}")

if allure_path:
    # 测试运行allure命令
    try:
        result = subprocess.run([allure_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
        print(f"Allure版本: {result.stdout.strip()}")
    except Exception as e:
        print(f"运行allure命令失败: {e}")
else:
    print("未找到allure命令")