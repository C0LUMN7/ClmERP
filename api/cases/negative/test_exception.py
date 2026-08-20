import allure
import pytest
import requests
import urllib3

urllib3.disable_warnings()

from api.framework.yaml_loader import load_case_pairs
from api.framework.runner import run_case
from shared.database import ConnectMysql
from shared.debugtalk import DebugTalk
from shared.test_data import m_id, c_id
from config.settings import get_api_url


@pytest.mark.negative
@allure.feature(next(m_id) + 'ERP异常场景测试')
class TestExceptionScenario:

    # ============================================================
    # 鉴权异常：绕过框架自动重登，直接用 requests 验证
    # ============================================================

    @allure.story(next(c_id) + '鉴权异常')
    def test_auth_token_empty(self):
        """Token为空访问写接口，不应写入成功"""
        host = get_api_url()
        dt = DebugTalk()
        order_no = f"AUTO_API_EX_AUTH_{dt.fixed_timestamp()}_EMPTY"

        allure.dynamic.title("Token为空-新增销售出库单")
        resp = requests.post(f"{host}/depotHead/addDepotHeadAndDetail",
            headers={"Content-Type": "application/json;charset=UTF-8"},
            json={
                "info": f'{{"number":"{order_no}","type":"出库","subType":"销售","organId":{dt.get_business_id("customer_organ_id")},"accountId":{dt.get_business_id("settle_account_id")},"totalPrice":29,"changeAmount":0,"debt":29,"discount":0,"discountMoney":0,"discountLastMoney":29,"otherMoney":0,"operTime":"2026-06-17 12:00:00","status":"0"}}',
                "rows": "[]"
            },
            verify=False, timeout=10)

        allure.attach(str(resp.status_code), "HTTP状态码")
        allure.attach(resp.text, "响应文本")
        assert resp.status_code != 200, f"期望非200状态码，实际{resp.status_code}"

        conn = ConnectMysql()
        try:
            rows = conn.query_all(
                f"SELECT id FROM jsh_depot_head WHERE number='{order_no}' AND delete_flag='0'")
            assert not rows, f"数据库不应存在单据{order_no}"
        finally:
            try:
                conn.close()
            except Exception:
                pass
        allure.attach("数据库未写入脏数据", "DB校验")

    @allure.story(next(c_id) + '鉴权异常')
    def test_auth_token_invalid(self):
        """Token无效访问写接口，不应写入成功"""
        host = get_api_url()
        dt = DebugTalk()
        order_no = f"AUTO_API_EX_AUTH_{dt.fixed_timestamp()}_INVALID"

        allure.dynamic.title("Token无效-新增销售出库单")
        resp = requests.post(f"{host}/depotHead/addDepotHeadAndDetail",
            headers={
                "Content-Type": "application/json;charset=UTF-8",
                "X-Access-Token": "invalid_token"
            },
            json={
                "info": f'{{"number":"{order_no}","type":"出库","subType":"销售","organId":{dt.get_business_id("customer_organ_id")},"accountId":{dt.get_business_id("settle_account_id")},"totalPrice":29,"changeAmount":0,"debt":29,"discount":0,"discountMoney":0,"discountLastMoney":29,"otherMoney":0,"operTime":"2026-06-17 12:00:00","status":"0"}}',
                "rows": "[]"
            },
            verify=False, timeout=10)

        allure.attach(str(resp.status_code), "HTTP状态码")
        allure.attach(resp.text, "响应文本")
        assert resp.status_code != 200, f"期望非200状态码，实际{resp.status_code}"

        conn = ConnectMysql()
        try:
            rows = conn.query_all(
                f"SELECT id FROM jsh_depot_head WHERE number='{order_no}' AND delete_flag='0'")
            assert not rows, f"数据库不应存在单据{order_no}"
        finally:
            try:
                conn.close()
            except Exception:
                pass
        allure.attach("数据库未写入脏数据", "DB校验")

    # ============================================================
    # 销售异常
    # ============================================================

    @allure.story(next(c_id) + '销售异常')
    @pytest.mark.parametrize(
        "base_info,testcase",
        load_case_pairs("./api/cases/negative/sales_exception.yml")
    )
    def test_sales_exception(self, base_info, testcase):
        allure.dynamic.title(testcase["case_name"])
        run_case(base_info, testcase, yaml_file="./api/cases/negative/sales_exception.yml")

    # ============================================================
    # 收付款异常
    # ============================================================

    @allure.story(next(c_id) + '超额收款边界场景')
    @pytest.mark.parametrize(
        "base_info,testcase",
        load_case_pairs("./api/cases/negative/payment_exception.yml")
    )
    def test_payment_exception(self, base_info, testcase):
        allure.dynamic.title(testcase["case_name"])
        run_case(base_info, testcase, yaml_file="./api/cases/negative/payment_exception.yml")
