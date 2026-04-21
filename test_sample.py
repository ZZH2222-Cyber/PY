import pytest
import allure

@allure.feature("API测试")
@allure.story("接口测试")
@allure.severity("normal")
def test_api_request():
    """API测试请求"""
    with allure.step("发送GET请求"):
        assert True