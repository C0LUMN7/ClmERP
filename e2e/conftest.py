# -*- coding: utf-8 -*-
"""跨层端到端用例 fixture。"""
import time
from pathlib import Path

import allure
import pytest

from config.settings import ERP_PASSWORD, ERP_UI_URL, ERP_USERNAME
from shared.api_client import ErpApiClient
from shared.db_helpers import cleanup_depot_documents, count_run_residue, list_depot_heads
from ui.pages.login_page import LoginPage

_AUTH_DIR = Path(__file__).resolve().parent.parent / ".runtime" / "auth"
_CONTEXT_ARGS = {
    "viewport": {"width": 1920, "height": 1080},
    "ignore_https_errors": True,
}


def pytest_runtest_call(item):
    if item.parent._obj.__doc__:
        allure.dynamic.feature(item.parent._obj.__doc__)
    if item.function.__doc__:
        allure.dynamic.title(item.function.__doc__)


def _missing_issues():
    issues = []
    if not ERP_UI_URL:
        issues.append("ERP UI 地址未配置")
    if not (ERP_USERNAME and ERP_PASSWORD):
        issues.append("测试账号未配置")
    login_missing = LoginPage.missing_materials()
    if login_missing:
        issues.append("登录页真实资料未齐：" + "、".join(login_missing))
    return issues


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    issues = _missing_issues()
    if issues:
        pytest.skip("无法真实运行跨层端到端用例：" + "；".join(issues))
    return {"args": ["--no-sandbox"], **browser_type_launch_args}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, e2e_login_state_path):
    args = {**_CONTEXT_ARGS, **browser_context_args}
    args["storage_state"] = str(e2e_login_state_path)
    return args


@pytest.fixture(scope="session")
def e2e_login_state_path(browser):
    _AUTH_DIR.mkdir(parents=True, exist_ok=True)
    state_file = _AUTH_DIR / f"e2e-login-{time.strftime('%Y%m%d-%H%M%S')}.json"
    context = browser.new_context(**_CONTEXT_ARGS)
    try:
        page = context.new_page()
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(ERP_USERNAME, ERP_PASSWORD)
        login_page.assert_logged_in()
        context.storage_state(path=str(state_file))
    finally:
        context.close()
    yield state_file


@pytest.fixture(scope="session")
def e2e_run_id() -> str:
    return time.strftime("%Y%m%d%H%M%S")


@pytest.fixture(scope="session")
def e2e_api_client():
    return ErpApiClient().login()


@pytest.fixture(scope="session", autouse=True)
def e2e_run_data_cleanup(e2e_run_id):
    yield
    prefix = "AUTO_E2E_"
    docs = list_depot_heads(prefix, e2e_run_id)
    audited_stock_docs = [
        row for row in docs
        if str(row.get("status")) == "1" and row.get("sub_type") in ("采购", "销售")
    ]
    reverse_failed = 0
    if audited_stock_docs:
        client = ErpApiClient().login()
        audited_stock_docs.sort(key=lambda row: 0 if row.get("type") == "出库" else 1)
        for row in audited_stock_docs:
            try:
                client.set_depot_head_status(row["id"], "0")
                print(f"[E2E 后置清理] 反审核单据: {row['number']} id={row['id']}")
            except Exception as exc:
                reverse_failed += 1
                print(f"[E2E 后置清理] 反审核失败: {row['number']} id={row['id']}，原因: {exc}")
    if reverse_failed:
        raise AssertionError(f"E2E 后置清理中止：{reverse_failed} 张已审核出入库单反审核失败")

    affected = cleanup_depot_documents(prefix, e2e_run_id)
    for label, count in affected.items():
        print(f"[E2E 后置清理] {label} 影响行数: {count}")
    residue = count_run_residue(prefix, e2e_run_id)
    print(f"[E2E 后置清理] 残留复核: {residue}, run_id={e2e_run_id}")
    if any(residue.values()):
        raise AssertionError(f"E2E 后置清理后仍存在有效残留: {residue}")
