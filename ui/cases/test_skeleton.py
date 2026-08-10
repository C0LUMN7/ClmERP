# -*- coding: utf-8 -*-
"""P0: UI 收集链路骨架用例

仅用于验证 `pytest ui --collect-only` 收集链路：不启动浏览器、不登录真实系统。
本用例不是 ERP 业务用例；正式 UI 用例待 P2 阶段由人工提供云端 jshERP 页面
操作、截图/录屏/codegen/DOM 等资料后实现。
"""


def test_ui_skeleton():
    """P0 骨架占位：验证 UI 用例可被 pytest 收集"""
    assert True
