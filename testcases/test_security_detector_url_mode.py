"""安全检测入口：URL 模式解析与无接口配置运行的冒烟测试。"""

import pytest


def test_build_interface_from_url_has_query_param() -> None:
    from testcases.security.run_detector import _build_interface_from_url

    base_url, cfg = _build_interface_from_url("https://example.com/get?q=1")
    assert base_url == "https://example.com"
    assert cfg["interface"] == "/get"
    assert cfg["method"] == "GET"
    assert cfg["param_type"] == "query"
    assert "q" in cfg["default_data"]


def test_build_interface_from_url_no_query_uses_default_q() -> None:
    from testcases.security.run_detector import _build_interface_from_url

    base_url, cfg = _build_interface_from_url("https://example.com/path")
    assert base_url == "https://example.com"
    assert cfg["interface"] == "/path"
    assert cfg["default_data"]["q"] == "test"


def test_run_detection_url_mode_invalid_returns_empty(monkeypatch) -> None:
    from testcases.security import run_detector

    # 避免真实网络请求：让 init_all_instances 抛异常
    monkeypatch.setattr(run_detector, "init_all_instances", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
    out = run_detector.run_detection("https://example.com/get?q=1", None)
    assert out == []

