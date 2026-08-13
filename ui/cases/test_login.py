# -*- coding: utf-8 -*-
"""ERP 登录冒烟测试

- 登录地址、账号、密码从 config/local.ini 或环境变量读取，用例内不硬编码凭据
- 登录成功判断条件必须来自真实 jshERP 页面资料（目标 URL、页面标题或稳定可见元素）
- 真实页面资料缺失时，本用例会在启动浏览器前被跳过并说明原因（见 ui/conftest.py），
  不会使用猜测的定位器或断言冒充真实登录通过
"""
import pytest

from config.settings import ERP_PASSWORD, ERP_USERNAME
from ui.pages.login_page import LoginPage


@pytest.mark.smoke
def test_login(fresh_page):
    """真实账号密码登录 jshERP，并校验配置的登录成功判断条件"""
    login_page = LoginPage(fresh_page)
    login_page.open()
    login_page.login(ERP_USERNAME, ERP_PASSWORD)
    login_page.assert_logged_in()
