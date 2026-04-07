#!/usr/bin/env python3
"""
运行测试的主入口文件
"""
import os
import subprocess
import sys

def run_tests():
    """
    运行测试
    """
    # 确保在项目根目录运行
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # 运行pytest测试
    print("开始运行测试...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "src/tests", "-v"],
        capture_output=True,
        text=True
    )
    
    # 将测试输出保存到文件
    with open("test_output.log", "w", encoding="utf-8") as f:
        f.write("测试输出:\n")
        f.write(result.stdout)
        if result.stderr:
            f.write("\n错误输出:\n")
            f.write(result.stderr)
    
    # 打印测试结果
    print("测试输出:")
    print(result.stdout)
    
    if result.stderr:
        print("错误输出:")
        print(result.stderr)
    
    print(f"测试结果: {'通过' if result.returncode == 0 else '失败'}")
    return result.returncode

def run_tests_with_allure():
    """
    运行测试并生成Allure报告
    """
    # 确保在项目根目录运行
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # 运行pytest测试并生成Allure报告
    print("开始运行测试并生成Allure报告...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "src/tests", "-v", "--alluredir=./allure-results"],
        capture_output=True,
        text=True
    )
    
    # 将测试输出保存到文件
    with open("test_output.log", "w", encoding="utf-8") as f:
        f.write("测试输出:\n")
        f.write(result.stdout)
        if result.stderr:
            f.write("\n错误输出:\n")
            f.write(result.stderr)
    
    # 打印测试结果
    print("测试输出:")
    print(result.stdout)
    
    if result.stderr:
        print("错误输出:")
        print(result.stderr)
    
    print(f"测试结果: {'通过' if result.returncode == 0 else '失败'}")
    
    # 检查是否安装了allure（首先尝试本地版本）
    try:
        # 设置Java路径
        java_path = "C:\\Program Files\\Java\\jdk-21.0.10\\bin\\java.exe"
        os.environ["JAVA_HOME"] = "C:\\Program Files\\Java\\jdk-21.0.10"
        
        # 尝试使用本地Allure版本
        allure_path = os.path.join(project_root, "allure-2.24.1", "bin", "allure.bat")
        
        # 检查Allure是否存在
        if os.path.exists(allure_path):
            print("使用本地Allure版本...")
            # 生成Allure报告
            print("生成Allure报告...")
            report_result = subprocess.run(
                [allure_path, "serve", "./allure-results"],
                capture_output=True,
                text=True,
                env=os.environ
            )
            print("Allure报告已生成并在浏览器中打开")
        else:
            print("未找到Allure，无法生成报告。")
    except Exception as e:
        print(f"运行Allure时出错: {str(e)}")
    
    return result.returncode

if __name__ == "__main__":
    # 运行测试
    if len(sys.argv) > 1 and sys.argv[1] == "--allure":
        run_tests_with_allure()
    else:
        run_tests()
