# -*- coding: utf-8 -*-
"""P0: UI 自动化技术骨架（从 playwright-ui 精简迁移）

迁移自 /home/column/code/playwright-ui（仅技术骨架，不含非 ERP 业务用例）：
1. pytest_runtest_call: 根据 docstring 动态设置 Allure feature/title
2. browser_type_launch_args / browser_context_args: 浏览器与 Context 启动参数
3. unlogin_context / unlogin_page: 独立 BrowserContext，失败截图、视频与 Allure 附件
4. 登录状态复用（storage_state）思路：P2 配合官方 pytest-playwright 实现

P0 边界说明：
- 本文件顶层不导入 playwright（P0 尚未引入官方 pytest-playwright 依赖）
- 骨架 fixture 在函数体内延迟导入，P2 引入官方依赖后即可启用
- P0 不启动浏览器、不登录真实系统、不含任何真实 ERP UI 业务用例
"""
import os
from typing import Any, Dict, List

import allure
import pytest


def pytest_runtest_call(item):
    """动态添加 allure feature/title（从 playwright-ui 根 conftest.py 迁移）"""
    if item.parent._obj.__doc__:
        allure.dynamic.feature(item.parent._obj.__doc__)
    if item.function.__doc__:
        allure.dynamic.title(item.function.__doc__)


# ---------------------------------------------------------------------------
# Playwright fixture 技术骨架（依赖官方 pytest-playwright，P2 启用）
# fixture 仅在用例请求时执行，收集阶段不会触发浏览器启动
# ---------------------------------------------------------------------------


def _build_artifact_test_folder(pytestconfig: Any, request: pytest.FixtureRequest, folder_or_file_name: str) -> str:
    """构建截图/视频产物目录（从 playwright-ui cases/conftest.py 迁移）"""
    from slugify import slugify  # 延迟导入，P0 未安装依赖时不影响收集
    output_dir = pytestconfig.getoption("--output")
    return os.path.join(output_dir, slugify(request.node.nodeid), folder_or_file_name)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """浏览器启动参数：窗口最大化（从 playwright-ui 根 conftest.py 迁移）"""
    return {"args": ['--start-maximized'], **browser_type_launch_args}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Context 参数：无视口限制、忽略 HTTPS 证书错误（从 playwright-ui 根 conftest.py 迁移）"""
    return {
        "no_viewport": True,
        "ignore_https_errors": True,
        **browser_context_args,
    }


@pytest.fixture(scope="module")
def unlogin_context(browser, pytestconfig, browser_context_args: Dict):
    """
    登录注册等不依赖登录状态的页面使用独立 Context，避免全局登录 Cookie 干扰
    （从 playwright-ui cases/conftest.py 迁移）
    """
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture
def unlogin_page(unlogin_context, pytestconfig: Any, request: pytest.FixtureRequest):
    """
    独立 Context 下的 Page，带失败截图、视频和 Allure 附件
    （从 playwright-ui cases/conftest.py 迁移）
    """
    from playwright.sync_api import Error  # 延迟导入，P0 未安装依赖时不影响收集

    pages: List = []
    unlogin_context.on("page", lambda page: pages.append(page))
    page = unlogin_context.new_page()
    yield page
    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else True
    # 截图判断
    screenshot_option = pytestconfig.getoption("--screenshot")
    capture_screenshot = screenshot_option == "on" or (failed and screenshot_option == "only-on-failure")
    if capture_screenshot:
        for index, page in enumerate(pages):
            human_readable_status = "failed" if failed else "finished"
            screenshot_path = _build_artifact_test_folder(
                pytestconfig, request, f"test-{human_readable_status}-{index + 1}.png"
            )
            try:
                page.screenshot(timeout=5000, path=screenshot_path)
                # 把截图放入 allure 报告
                allure.attach.file(screenshot_path,
                                   name=f"{request.node.name}-{human_readable_status}-{index + 1}",
                                   attachment_type=allure.attachment_type.PNG)
            except Error:
                pass
    page.close()
    # 用例添加视频
    video_option = pytestconfig.getoption("--video")
    preserve_video = video_option == "on" or (failed and video_option == "retain-on-failure")
    if preserve_video:
        for page in pages:
            video = page.video
            if not video:
                continue
            try:
                video_path = video.path()
                file_name = os.path.basename(video_path)
                file_path = _build_artifact_test_folder(pytestconfig, request, file_name)
                video.save_as(path=file_path)
                allure.attach.file(file_path, name=f"{request.node.name}-{human_readable_status}-{index + 1}",
                                   attachment_type=allure.attachment_type.WEBM)
            except Error:
                # Silent catch empty videos.
                pass


# ---------------------------------------------------------------------------
# 登录状态复用（P2 实现，当前仅记录思路，不编写代码）
# 1. session 开始时登录一次并保存 storage_state 到 .runtime/auth/
# 2. 每条测试创建独立 BrowserContext 并加载已登录状态
# 3. 测试结束关闭自己的 Context，避免页面、Cookie、LocalStorage 互相污染
# ---------------------------------------------------------------------------
