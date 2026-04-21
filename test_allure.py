import os
import json
import uuid
import time
import tempfile
import subprocess

# 创建临时目录
temp_dir = tempfile.mkdtemp()
print(f"临时目录: {temp_dir}")

# 创建allure-results目录
allure_results_dir = os.path.join(temp_dir, 'allure-results')
os.makedirs(allure_results_dir, exist_ok=True)
print(f"allure-results目录: {allure_results_dir}")

# 创建测试结果JSON文件（使用pytest-allure格式）
test_uuid = str(uuid.uuid4())
test_result = {
    "name": "test_api_request",
    "fullName": "test_sample#test_api_request",
    "status": "passed",
    "description": "API测试请求",
    "start": int(time.time() * 1000),
    "stop": int((time.time() + 1) * 1000),
    "uuid": test_uuid,
    "historyId": str(uuid.uuid4()),
    "testCaseId": str(uuid.uuid4()),
    "steps": [
        {
            "name": "发送GET请求",
            "status": "passed",
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
        {"name": "suite", "value": "test_sample"},
        {"name": "host", "value": "victor"},
        {"name": "thread", "value": "MainThread"},
        {"name": "framework", "value": "pytest"},
        {"name": "language", "value": "cpython3"},
        {"name": "package", "value": "test_sample"}
    ]
}

# 写入测试结果文件（文件名格式：{uuid}-result.json）
result_file = os.path.join(allure_results_dir, f"{test_uuid}-result.json")
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(test_result, f, ensure_ascii=False, indent=2)

print(f"已创建测试结果文件: {result_file}")

# 列出allure-results目录中的文件
print(f"\nallure-results目录中的文件:")
for f in os.listdir(allure_results_dir):
    print(f"  - {f}")

# 生成Allure报告
allure_report_dir = os.path.join(temp_dir, 'allure-report')
allure_path = 'D:\\Documents\\allure报告\\allure-2.38.1\\bin\\allure.bat'
allure_cmd = [allure_path, 'generate', allure_results_dir, '-o', allure_report_dir, '--clean']

print(f"\n运行allure命令: {' '.join(allure_cmd)}")

try:
    process = subprocess.Popen(allure_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = process.communicate(timeout=30)

    print(f"\nallure stdout:\n{stdout}")
    print(f"\nallure stderr:\n{stderr}")
    print(f"\nallure返回码: {process.returncode}")

    if process.returncode == 0:
        print("\nAllure报告生成成功!")

        # 检查报告目录
        print(f"\n报告目录中的文件:")
        for root, dirs, files in os.walk(allure_report_dir):
            for f in files:
                filepath = os.path.join(root, f)
                print(f"  - {filepath}")

        # 检查summary.json
        summary_file = os.path.join(allure_report_dir, 'widgets', 'summary.json')
        if os.path.exists(summary_file):
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            print(f"\nsummary.json内容: {json.dumps(summary, indent=2)}")
    else:
        print("\nAllure报告生成失败!")
except Exception as e:
    print(f"\n执行allure命令时出错: {e}")

# 不删除临时目录，以便检查
print(f"\n临时目录未删除，可用于检查: {temp_dir}")