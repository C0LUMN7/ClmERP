# -*- coding: utf-8 -*-
"""ERP UI Page Object 基类

只提供各页面对象共用的最小能力：打开页面、等待 URL、等待标题与等待可见文本。
定位器统一优先使用 role、label、text 和稳定属性，不依赖易变化的 CSS 层级。
"""
from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str) -> None:
        """打开指定地址并等待页面加载"""
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")

    def wait_for_url(self, url: str, timeout: int = 10000) -> None:
        """等待页面 URL 满足匹配（支持 '**/index' 这类 glob 表达式）"""
        self.page.wait_for_url(url, timeout=timeout)

    def wait_for_title(self, title: str, timeout: int = 10000) -> None:
        """等待页面标题与预期一致"""
        expect(self.page).to_have_title(title, timeout=timeout)

    def wait_visible_text(self, text: str, timeout: int = 10000) -> None:
        """等待包含指定文本的元素可见（可用于登录成功等稳定判断）"""
        expect(self.page.get_by_text(text).first).to_be_visible(timeout=timeout)
