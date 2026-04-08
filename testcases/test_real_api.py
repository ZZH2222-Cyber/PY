# testcases/test_real_api.py
"""真实接口测试用例：使用 httpbin.org 进行真实 HTTP 请求测试。"""

import json
import logging
from typing import Any, Dict

import allure
import pytest

from core.request_handler import RequestHandler

logger = logging.getLogger(__name__)


@allure.feature("HTTP请求测试")
@allure.story("GET请求")
class TestGetRequest:
    """GET 请求测试类。"""

    @allure.title("GET请求-基本查询")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_basic(self) -> None:
        """测试基本 GET 请求。

        验证点：
        - HTTP 状态码为 200
        - 响应包含 args 字段
        """
        client = RequestHandler()
        response = client.get("/get")
        
        assert response.status_code == 200, f"状态码期望 200，实际 {response.status_code}"
        
        data = response.json()
        assert "args" in data, "响应应包含 args 字段"
        
        allure.attach(json.dumps(data, ensure_ascii=False, indent=2), name="响应数据", attachment_type=allure.attachment_type.JSON)

    @allure.title("GET请求-带查询参数")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_with_params(self) -> None:
        """测试带查询参数的 GET 请求。

        验证点：
        - 参数正确传递
        - 响应中包含传入的参数
        """
        client = RequestHandler()
        params = {"page": "1", "size": "10", "keyword": "test"}
        response = client.get("/get", params=params)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["args"]["page"] == "1", "page 参数应为 1"
        assert data["args"]["size"] == "10", "size 参数应为 10"
        assert data["args"]["keyword"] == "test", "keyword 参数应为 test"

    @allure.title("GET请求-自定义请求头")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_with_headers(self) -> None:
        """测试带自定义请求头的 GET 请求。

        验证点：
        - 自定义请求头正确传递
        """
        client = RequestHandler()
        headers = {"X-Custom-Header": "test-value-123", "X-Request-Id": "req-001"}
        response = client.get("/headers", headers=headers)
        
        assert response.status_code == 200
        
        data = response.json()
        assert "X-Custom-Header" in data["headers"], "应包含自定义请求头"
        assert data["headers"]["X-Custom-Header"] == "test-value-123"


@allure.feature("HTTP请求测试")
@allure.story("POST请求")
class TestPostRequest:
    """POST 请求测试类。"""

    @allure.title("POST请求-JSON格式")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_post_json(self) -> None:
        """测试 JSON 格式的 POST 请求。

        验证点：
        - JSON 数据正确传递
        - 响应中包含发送的数据
        """
        client = RequestHandler()
        payload = {
            "username": "admin",
            "password": "123456",
            "remember": True
        }
        response = client.post("/post", json=payload)
        
        assert response.status_code == 200
        
        data = response.json()
        assert "json" in data, "响应应包含 json 字段"
        assert data["json"]["username"] == "admin"
        assert data["json"]["password"] == "123456"
        assert data["json"]["remember"] is True
        
        allure.attach(json.dumps(payload, ensure_ascii=False, indent=2), name="请求数据", attachment_type=allure.attachment_type.JSON)

    @allure.title("POST请求-表单格式")
    @allure.severity(allure.severity_level.NORMAL)
    def test_post_form(self) -> None:
        """测试表单格式的 POST 请求。

        验证点：
        - 表单数据正确传递
        """
        client = RequestHandler()
        form_data = {"username": "testuser", "password": "testpass"}
        response = client.post("/post", data=form_data)
        
        assert response.status_code == 200
        
        data = response.json()
        assert "form" in data
        assert data["form"]["username"] == "testuser"
        assert data["form"]["password"] == "testpass"

    @allure.title("POST请求-嵌套JSON")
    @allure.severity(allure.severity_level.NORMAL)
    def test_post_nested_json(self) -> None:
        """测试嵌套 JSON 数据的 POST 请求。

        验证点：
        - 嵌套结构正确传递
        """
        client = RequestHandler()
        payload = {
            "user": {
                "name": "张三",
                "age": 25,
                "address": {
                    "city": "北京",
                    "street": "朝阳区"
                }
            },
            "orders": [
                {"id": 1, "product": "手机"},
                {"id": 2, "product": "电脑"}
            ]
        }
        response = client.post("/post", json=payload)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["json"]["user"]["name"] == "张三"
        assert data["json"]["user"]["address"]["city"] == "北京"
        assert len(data["json"]["orders"]) == 2


@allure.feature("HTTP请求测试")
@allure.story("PUT请求")
class TestPutRequest:
    """PUT 请求测试类。"""

    @allure.title("PUT请求-更新数据")
    @allure.severity(allure.severity_level.NORMAL)
    def test_put_json(self) -> None:
        """测试 PUT 请求更新数据。

        验证点：
        - PUT 方法正确执行
        - 数据正确传递
        """
        client = RequestHandler()
        payload = {"id": 1, "name": "更新后的名称", "status": "active"}
        response = client.put("/put", json=payload)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["json"]["id"] == 1
        assert data["json"]["name"] == "更新后的名称"


@allure.feature("HTTP请求测试")
@allure.story("DELETE请求")
class TestDeleteRequest:
    """DELETE 请求测试类。"""

    @allure.title("DELETE请求-删除资源")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete(self) -> None:
        """测试 DELETE 请求。

        验证点：
        - DELETE 方法正确执行
        """
        client = RequestHandler()
        response = client.delete("/delete")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "url" in data
        assert "/delete" in data["url"]


@allure.feature("HTTP状态码测试")
@allure.story("状态码验证")
class TestStatusCode:
    """HTTP 状态码测试类。"""

    @allure.title("状态码-200成功")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_status_200(self) -> None:
        """测试 200 状态码。"""
        client = RequestHandler()
        response = client.get("/status/200")
        assert response.status_code == 200

    @allure.title("状态码-201创建成功")
    @allure.severity(allure.severity_level.NORMAL)
    def test_status_201(self) -> None:
        """测试 201 状态码。"""
        client = RequestHandler()
        response = client.get("/status/201")
        assert response.status_code == 201

    @allure.title("状态码-400错误请求")
    @allure.severity(allure.severity_level.NORMAL)
    def test_status_400(self) -> None:
        """测试 400 状态码。"""
        client = RequestHandler()
        response = client.get("/status/400")
        assert response.status_code == 400

    @allure.title("状态码-404未找到")
    @allure.severity(allure.severity_level.NORMAL)
    def test_status_404(self) -> None:
        """测试 404 状态码。"""
        client = RequestHandler()
        response = client.get("/status/404")
        assert response.status_code == 404

    @allure.title("状态码-500服务器错误")
    @allure.severity(allure.severity_level.NORMAL)
    def test_status_500(self) -> None:
        """测试 500 状态码。"""
        client = RequestHandler()
        response = client.get("/status/500")
        assert response.status_code == 500


@allure.feature("认证测试")
@allure.story("Basic认证")
class TestBasicAuth:
    """Basic 认证测试类。"""

    @allure.title("Basic认证-成功")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_basic_auth_success(self) -> None:
        """测试 Basic 认证成功场景。

        验证点：
        - 正确的用户名密码能通过认证
        """
        client = RequestHandler()
        response = client.get("/basic-auth/admin/123456", auth=("admin", "123456"))
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"] == "admin"

    @allure.title("Basic认证-失败")
    @allure.severity(allure.severity_level.NORMAL)
    def test_basic_auth_failure(self) -> None:
        """测试 Basic 认证失败场景。

        验证点：
        - 错误的密码返回 401
        """
        client = RequestHandler()
        response = client.get("/basic-auth/admin/123456", auth=("admin", "wrongpass"))
        
        assert response.status_code == 401


@allure.feature("响应测试")
@allure.story("响应格式")
class TestResponseFormat:
    """响应格式测试类。"""

    @allure.title("响应-JSON格式验证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_json_response(self) -> None:
        """测试 JSON 响应格式。

        验证点：
        - 响应是有效的 JSON
        - 包含必要的字段
        """
        client = RequestHandler()
        response = client.get("/get")
        
        assert response.headers.get("Content-Type", "").startswith("application/json")
        
        data = response.json()
        required_fields = ["args", "headers", "origin", "url"]
        for field in required_fields:
            assert field in data, f"响应应包含 {field} 字段"

    @allure.title("响应-IP地址获取")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_ip(self) -> None:
        """测试获取客户端 IP。

        验证点：
        - 返回有效的 IP 地址
        """
        client = RequestHandler()
        response = client.get("/origin")
        
        assert response.status_code == 200
        
        ip = response.text.strip()
        # 简单验证 IP 格式
        parts = ip.split(".")
        assert len(parts) == 4, f"应返回有效的 IPv4 地址，实际: {ip}"
        for part in parts:
            assert part.isdigit() and 0 <= int(part) <= 255


@allure.feature("边界测试")
@allure.story("数据边界")
class TestBoundary:
    """边界条件测试类。"""

    @allure.title("边界-空JSON")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_json(self) -> None:
        """测试空 JSON 请求体。"""
        client = RequestHandler()
        response = client.post("/post", json={})
        
        assert response.status_code == 200
        assert response.json()["json"] == {}

    @allure.title("边界-特殊字符")
    @allure.severity(allure.severity_level.NORMAL)
    def test_special_characters(self) -> None:
        """测试特殊字符处理。

        验证点：
        - 中文、emoji 等特殊字符正确传递
        """
        client = RequestHandler()
        payload = {
            "chinese": "你好世界",
            "emoji": "🎉🎊🎁",
            "special": "<>&\"'"
        }
        response = client.post("/post", json=payload)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["json"]["chinese"] == "你好世界"
        assert data["json"]["emoji"] == "🎉🎊🎁"

    @allure.title("边界-长字符串")
    @allure.severity(allure.severity_level.NORMAL)
    def test_long_string(self) -> None:
        """测试长字符串处理。"""
        client = RequestHandler()
        long_text = "A" * 10000
        payload = {"long_text": long_text}
        response = client.post("/post", json=payload)
        
        assert response.status_code == 200
        assert response.json()["json"]["long_text"] == long_text
