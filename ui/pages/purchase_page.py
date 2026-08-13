# -*- coding: utf-8 -*-
"""采购管理页面对象

定位器来自云端 jshERP 采购页面真实 DOM 与只读式页面资料收集：
采购管理 > 采购订单，前端路由 /bill/purchase_order；
采购管理 > 采购入库，前端路由 /bill/purchase_in。
"""
from playwright.sync_api import expect

from config.settings import ERP_UI_URL
from ui.pages.base_page import BasePage


class PurchasePage(BasePage):
    """采购页面：采购订单新增、审核并转未审核采购入库"""

    PURCHASE_ORDER_ROUTE = "/bill/purchase_order"
    PURCHASE_IN_ROUTE = "/bill/purchase_in"
    SUPPLIER_NAME = "自动化测试专用供应商"
    WAREHOUSE_NAME = "自动化测试专属仓库3"
    PRODUCT_NAME = "请购单测试商品C"
    QUANTITY = "1"
    UNIT_PRICE = "30"

    def open_purchase_order(self) -> None:
        """进入采购订单列表页"""
        self._push_route(self.PURCHASE_ORDER_ROUTE)
        expect(self.page.get_by_role("button", name="新增")).to_be_visible(timeout=15000)

    def create_unapproved_order(self, order_no: str) -> None:
        """新增采购订单并保存为未审核状态"""
        self.open_purchase_order()
        self.page.get_by_role("button", name="新增").click()
        self._close_intro()
        expect(self.page.get_by_text("供应商").last).to_be_visible(timeout=10000)

        self._select_ant_option("请选择供应商", self.SUPPLIER_NAME)
        self.page.locator("#number").fill(order_no)
        self._select_ant_option("输入条码或名称", self.PRODUCT_NAME)
        self._overwrite_input(self.page.locator("[id^='operNumber_']").first, self.QUANTITY)
        self._overwrite_input(self.page.locator("[id^='unitPrice_']").first, self.UNIT_PRICE)
        self.page.get_by_role("button", name="保存（Ctrl+S）").click()
        self._wait_saved_row(order_no)

    def assert_order_unapproved(self, order_no: str) -> None:
        """按单号查询并断言采购订单为未审核"""
        self.assert_order_status(order_no, "未审核")

    def audit_order(self, order_no: str) -> None:
        """审核采购订单，并断言状态变为已审核"""
        self._select_order(order_no)
        self._click_toolbar_button("审核")
        self._confirm_operation()
        self.assert_order_status(order_no, "已审核")

    def reverse_audit_order(self, order_no: str) -> None:
        """反审核采购订单，并断言状态恢复为未审核"""
        self._select_order(order_no)
        self._click_toolbar_button("反审核")
        self._confirm_operation()
        self.assert_order_status(order_no, "未审核")

    def transfer_to_purchase_in(self, order_no: str, inbound_no: str) -> None:
        """把已审核采购订单转为未审核采购入库单"""
        self._select_order(order_no)
        self._click_toolbar_button("转采购入库")
        dialog = self._transfer_dialog("转采购入库")
        dialog.locator("#number").fill(inbound_no)
        self._select_dialog_warehouse(dialog)
        self._overwrite_input(dialog.locator("#changeAmount"), "0")
        dialog.get_by_role("button", name="保存（Ctrl+S）").click()
        expect(dialog).to_be_hidden(timeout=15000)
        self.assert_order_status(order_no, "完成采购")
        self.assert_purchase_in_unapproved(inbound_no)

    def assert_purchase_in_unapproved(self, inbound_no: str) -> None:
        """按单号查询并断言采购入库单为未审核"""
        row = self._query_purchase_in(inbound_no)
        expect(row).to_contain_text(self.SUPPLIER_NAME)
        expect(row).to_contain_text(self.PRODUCT_NAME)
        expect(row).to_contain_text("未审核")

    def assert_order_status(self, order_no: str, status: str) -> None:
        """按单号查询并断言采购订单状态"""
        row = self._query_order(order_no)
        expect(row).to_contain_text(self.SUPPLIER_NAME)
        expect(row).to_contain_text(self.PRODUCT_NAME)
        expect(row).to_contain_text(status)

    def _query_order(self, order_no: str):
        self.open_purchase_order()
        self.page.get_by_placeholder("请输入单据编号").first.fill(order_no)
        self.page.get_by_role("button", name="查 询").click()
        row = self.page.locator(".ant-table-tbody tr").filter(has_text=order_no).first
        expect(row).to_be_visible(timeout=15000)
        return row

    def _query_purchase_in(self, inbound_no: str):
        self._push_route(self.PURCHASE_IN_ROUTE)
        expect(self.page.get_by_role("button", name="新增")).to_be_visible(timeout=15000)
        self.page.get_by_placeholder("请输入单据编号").first.fill(inbound_no)
        self.page.get_by_role("button", name="查 询").click()
        row = self.page.locator(".ant-table-tbody tr").filter(has_text=inbound_no).first
        expect(row).to_be_visible(timeout=15000)
        return row

    def _select_order(self, order_no: str) -> None:
        row = self._query_order(order_no)
        checkbox = row.locator(".ant-checkbox-input").first
        if not checkbox.is_checked():
            checkbox.click()

    def _click_toolbar_button(self, name: str) -> None:
        buttons = self.page.locator("button:visible")
        for index in range(buttons.count()):
            button = buttons.nth(index)
            if button.inner_text().strip() == name:
                button.click()
                return
        raise RuntimeError(f"未找到工具栏按钮: {name}")

    def _confirm_operation(self) -> None:
        confirm = self.page.locator(".ant-modal:visible").filter(has_text="确认操作").first
        expect(confirm).to_be_visible(timeout=10000)
        confirm.get_by_role("button", name="确 定").click()

    def _transfer_dialog(self, title: str):
        dialog = self.page.get_by_role("dialog").filter(has_text=title).first
        expect(dialog).to_be_visible(timeout=10000)
        self._close_intro()
        return dialog

    def _select_dialog_warehouse(self, dialog) -> None:
        warehouse_select = dialog.get_by_role("combobox").nth(1)
        expect(warehouse_select).to_be_visible(timeout=10000)
        warehouse_select.click(force=True)
        self.page.keyboard.type(self.WAREHOUSE_NAME)
        option = self.page.locator(
            ".ant-select-dropdown:visible .ant-select-dropdown-menu-item"
        ).filter(has_text=self.WAREHOUSE_NAME).first
        expect(option).to_be_visible(timeout=10000)
        option.click()

    def _push_route(self, route: str) -> None:
        if self.page.url == "about:blank":
            self.page.goto(ERP_UI_URL.rstrip("/") + "/")
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(1200)
        self.page.evaluate(
            """async (path) => {
                const root = document.querySelector('#app') || document.querySelector('#root');
                const router = (window.app && window.app.$router)
                    || (root && root.__vue__ && root.__vue__.$router);
                if (!router) throw new Error('Vue router not found');
                await router.push(path);
            }""",
            route,
        )
        self.page.wait_for_timeout(1200)
        self._close_intro()

    def _select_ant_option(self, placeholder: str, option_text: str) -> None:
        self.page.get_by_text(placeholder).last.click()
        self.page.keyboard.type(option_text)
        option = self.page.locator(
            ".ant-select-dropdown:visible .ant-select-dropdown-menu-item"
        ).filter(has_text=option_text).first
        expect(option).to_be_visible(timeout=10000)
        option.click()

    def _overwrite_input(self, locator, value: str) -> None:
        locator.click()
        self.page.keyboard.press("Control+A")
        self.page.keyboard.type(value)

    def _close_intro(self) -> None:
        skip = self.page.locator(".introjs-skipbutton")
        if skip.count():
            try:
                skip.first.click(timeout=1000)
            except Exception:
                pass

    def _wait_saved_row(self, order_no: str) -> None:
        row = self.page.locator(".ant-table-tbody tr").filter(has_text=order_no).first
        expect(row).to_be_visible(timeout=15000)
