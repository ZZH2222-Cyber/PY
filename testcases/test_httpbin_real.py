# testcases/test_httpbin_real.py
"""真实场景测试：使用 httpbin.org 公共API进行接口测试。"""

import json
import logging
from typing import Any, Dict

import allure
import pytest

from core.request_handler import RequestHandler

logger = logging.getLogger(__name__)


@allure.feature("HTTP方法测试")
class TestHttpMethods:
    """测试各种HTTP方法。"""

    def setup_method(self) -> None:
        """每个测试方法前初始化客户端。

        参数：
            无

        返回：
            无
        """
        self.client = RequestHandler()

    @allure.story("GET请求")
    @allure.title("GET请求-基础测试")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_request(self) -> None:
        """测试GET请求能正确返回查询参数。

        参数：
            无

        返回：
            无

        异常：
            AssertionError: 断言失败时抛出。
        """
        params = {"name": "test", "value": "123"}
        response = self.client.get("/get", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["args"]["name"] == "test"
        assert data["args"]["value"] == "123"
        
        allure.attach(json.dumps(data, ensure_ascii=False, indent=2), name="响应数据", attachment_type=allure.attachment_type.JSON)

    @allure.story("POST请求")
    @allure.title("POST请求-JSON数据")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_post_json(self) -> None:
        """测试POST请求发送JSON数据。

        参数：
            无

        返回：
            无

        异常：
            AssertionError: 断言失败时抛出。
        """
        payload = {"username": "admin", "password": "secret123"}
        response = self.client.post("/post", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["json"]["username"] == "admin"
        assert data["json"]["password"] == "secret123"

    @allure.story("PUT请求")
    @allure.title("PUT请求-更新数据")
    @allure.severity(allure.severity_level.NORMAL)
    def test_put_request(self) -> None:
        """测试PUT请求更新数据。

        参数：
            无

        返回：
            无

        异常：
            AssertionError: 断言失败时抛出。
        """
        payload = {"id": 1, "name": "updated_name"}
        response = self.client.put("/put", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["json"]["id"] == 1

    @allure.story("DELETE请求")
    @allure.title("DELETE请求-删除资源")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_request(self) -> None:
        """测试DELETE请求删除资源。

        参数：
            无

        返回：
            无

        异常：
            AssertionError: 断言失败时抛出。
        """
        response = self.client.delete("/delete")
        
        assert response.status_code == 200


@allure.feature("状态码测试")
class TestStatusCodes:
    """测试各种HTTP状态码。"""

    def setup_method(self) -> None:
        """初始化客户端。"""
        self.client = RequestHandler()

    @allure.story("成功状态码")
    @allure.title("状态码200")
    def test_status_200(self) -> None:
        """测试返回200状态码。"""
        response = self.client.get("/status/200")
        assert response.status_code == 200

    @allure.story("重定向状态码")
    @allure.title("状态码301重定向")
    def test_status_301(self) -> None:
        """测试返回301状态码（禁用自动重定向）。"""
        response = self.client.get("/status/301", allow_redirects=False)
        assert response.status_code == 301

    @allure.story("客户端错误状态码")
    @allure.title("状态码404")
    def test_status_404(self) -> None:
        """测试返回404状态码。"""
        response = self.client.get("/status/404")
        assert response.status_code == 404

    @allure.story("服务端错误状态码")
    @allure.title("状态码500")
    def test_status_500(self) -> None:
        """测试返回500状态码。"""
        response = self.client.get("/status/500")
        assert response.status_code == 500


@allure.feature("请求头测试")
class TestHeaders:
    """测试自定义请求头。"""

    def setup_method(self) -> None:
        """初始化客户端。"""
        self.client = RequestHandler()

    @allure.story("自定义请求头")
    @allure.title("发送自定义Header")
    @allure.severity(allure.severity_level.NORMAL)
    def test_custom_headers(self) -> None:
        """测试发送自定义请求头。"""
        custom_headers = {
            "X-Custom-Header": "custom-value",
        }
        response = self.client.get("/headers", headers=custom_headers)
        
        assert response.status_code == 200
        data = response.json()
        # httpbin 返回的 header 名可能为小写，需要不区分大小写比较
        headers_lower = {k.lower(): v for k, v in data["headers"].items()}
        assert headers_lower.get("x-custom-header") == "custom-value"

    @allure.story("User-Agent")
    @allure.title("验证User-Agent头")
    def test_user_agent(self) -> None:
        """测试User-Agent请求头。"""
        response = self.client.get("/user-agent")
        
        assert response.status_code == 200
        data = response.json()
        assert "user-agent" in data


@allure.feature("响应数据测试")
class TestResponseData:
    """测试响应数据处理。"""

    def setup_method(self) -> None:
        """初始化客户端。"""
        self.client = RequestHandler()

    @allure.story("JSON响应")
    @allure.title("验证JSON响应格式")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_json_response(self) -> None:
        """测试JSON响应格式正确。"""
        response = self.client.get("/json")
        
        assert response.status_code == 200
        data = response.json()
        assert "slideshow" in data
        assert "title" in data["slideshow"]

    @allure.story("XML响应")
    @allure.title("验证XML响应")
    def test_xml_response(self) -> None:
        """测试XML响应。"""
        response = self.client.get("/xml")
        
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("Content-Type", "")


@allure.feature("Cookie测试")
class TestCookies:
    """测试Cookie处理。"""

    def setup_method(self) -> None:
        """初始化客户端。"""
        self.client = RequestHandler()

    @allure.story("设置Cookie")
    @allure.title("服务端设置Cookie")
    def test_set_cookie(self) -> None:
        """测试服务端设置Cookie。"""
        response = self.client.get("/cookies/set?session_id=abc123")
        
        assert response.status_code == 200

    @allure.story("获取Cookie")
    @allure.title("获取当前Cookies")
    def test_get_cookies(self) -> None:
        """测试获取当前Cookies。"""
        # 先设置cookie
        self.client.get("/cookies/set?test_cookie=test_value")
        # 再获取
        response = self.client.get("/cookies")
        
        assert response.status_code == 200
        data = response.json()
        assert "cookies" in data


@allure.feature("延迟响应测试")
class TestDelayedResponse:
    """测试延迟响应。"""

    def setup_method(self) -> None:
        """初始化客户端。"""
        self.client = RequestHandler()

    @allure.story("延迟响应")
    @allure.title("延迟1秒响应")
    @pytest.mark.slow
    def test_delayed_response_1s(self) -> None:
        """测试延迟1秒响应。"""
        response = self.client.get("/delay/1")
        
        assert response.status_code == 200

    @allure.story("延迟响应")
    @allure.title("延迟2秒响应")
    @pytest.mark.slow
    def test_delayed_response_2s(self) -> None:
        """测试延迟2秒响应。"""
        response = self.client.get("/delay/2")
        
        assert response.status_code == 200


@allure.feature("表单数据测试")
class TestFormData:
    """测试表单数据提交。"""

    def setup_method(self) -> None:
        """初始化客户端。"""
        self.client = RequestHandler()

    @allure.story("表单提交")
    @allure.title("POST表单数据")
    @allure.severity(allure.severity_level.NORMAL)
    def test_post_form_data(self) -> None:
        """测试POST表单数据。"""
        form_data = {"field1": "value1", "field2": "value2"}
        response = self.client.post("/post", data=form_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["form"]["field1"] == "value1"
        assert data["form"]["field2"] == "value2"

    @allure.story("文件上传")
    @allure.title("上传文件")
    def test_upload_file(self) -> None:
        """测试文件上传。"""
        files = {"file": ("test.txt", "Hello World!", "text/plain")}
        response = self.client.post("/post", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "files" in data


@allure.feature("参数化测试")
class TestParameterized:
    """参数化测试示例。"""

    def setup_method(self) -> None:
        """初始化客户端。"""
        self.client = RequestHandler()

    @allure.story("参数化查询")
    @allure.title("多组查询参数测试")
    @pytest.mark.parametrize("key,value", [
        ("name", "张三"),
        ("name", "John"),
        ("id", "123"),
        ("type", "user"),
    ])
    def test_query_params(self, key: str, value: str) -> None:
        """测试多组查询参数。

        参数：
            key: 参数名
            value: 参数值
        """
        params = {key: value}
        response = self.client.get("/get", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["args"][key] == value