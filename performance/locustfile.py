"""Locust read-only performance scenarios for jshERP."""

import json
import time

import urllib3
from locust import HttpUser, between, task
from locust.exception import StopUser

from shared.debugtalk import DebugTalk
from config.settings import ERP_PASSWORD, ERP_USERNAME, get_api_url


READONLY_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
}


class ErpReadOnlyUser(HttpUser):
    """Read-only Locust user for product, stock and document list queries."""

    host = get_api_url()
    wait_time = between(1, 3)

    def on_start(self) -> None:
        self.token = ""
        self._login()

    def _login(self) -> None:
        if not self.host:
            raise StopUser("ERP API address is not configured")
        if not ERP_USERNAME or not ERP_PASSWORD:
            raise StopUser("ERP login credentials are not configured")

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        helper = DebugTalk()
        for attempt in range(5):
            DebugTalk._captcha_data = None
            payload = {
                "loginName": ERP_USERNAME,
                "password": helper.md5_encryption(ERP_PASSWORD),
                "code": helper.get_captcha_code(),
                "uuid": helper.get_captcha_uuid(),
            }
            with self.client.post(
                "/user/login",
                json=payload,
                headers=READONLY_HEADERS,
                name="/user/login",
                catch_response=True,
                verify=False,
                timeout=15,
            ) as response:
                token = self._extract_token(response)
                if token:
                    self.token = token
                    response.success()
                    return
                if attempt == 4:
                    response.failure("ERP login failed")
                else:
                    response.success()
            time.sleep(1)
        raise StopUser("ERP login failed after retries")

    def _headers(self) -> dict:
        headers = dict(READONLY_HEADERS)
        headers["X-Access-Token"] = self.token
        return headers

    @staticmethod
    def _extract_token(response) -> str:
        if response.status_code != 200:
            return ""
        try:
            data = response.json()
        except ValueError:
            return ""
        if data.get("code") != 200:
            return ""
        token = data.get("data", {}).get("token")
        return token or ""

    @staticmethod
    def _validate_response(response, required_data_keys=()) -> bool:
        if response.status_code != 200:
            response.failure(f"HTTP status is {response.status_code}")
            return False
        if response.text and response.text.strip() == "loginOut":
            response.failure("ERP token expired")
            return False
        try:
            data = response.json()
        except ValueError:
            response.failure("response is not JSON")
            return False
        if data.get("code") != 200:
            response.failure("business code is not 200")
            return False
        payload = data.get("data")
        if not isinstance(payload, dict):
            response.failure("response data is not an object")
            return False
        for key in required_data_keys:
            if key not in payload:
                response.failure(f"response data missing key: {key}")
                return False
        response.success()
        return True

    def _get_readonly(self, path: str, *, name: str, params: dict, required_data_keys=()) -> None:
        if not self.token:
            self._login()
        with self.client.get(
            path,
            params=params,
            headers=self._headers(),
            name=name,
            catch_response=True,
            verify=False,
            timeout=15,
        ) as response:
            ok = self._validate_response(response, required_data_keys=required_data_keys)
            if not ok and response.text and response.text.strip() == "loginOut":
                self.token = ""

    @task(5)
    def query_material_list(self) -> None:
        self._get_readonly(
            "/material/list",
            name="/material/list",
            params={"currentPage": 1, "pageSize": 10},
            required_data_keys=("rows",),
        )

    @task(4)
    def query_material_stock(self) -> None:
        self._get_readonly(
            "/material/getListWithStock",
            name="/material/getListWithStock",
            params={
                "currentPage": 1,
                "pageSize": 10,
                "materialParam": "",
                "zeroStock": "0",
            },
            required_data_keys=("rows", "total"),
        )

    @task(3)
    def query_depot_head_list(self) -> None:
        search = {
            "type": "入库",
            "subType": "采购订单",
            "roleType": "全部数据",
            "status": "",
            "number": "",
            "beginTime": "",
            "endTime": "",
            "materialParam": "",
            "depotIds": "",
        }
        self._get_readonly(
            "/depotHead/list",
            name="/depotHead/list",
            params={
                "search": json.dumps(search, ensure_ascii=False),
                "currentPage": 1,
                "pageSize": 10,
            },
            required_data_keys=("rows", "total"),
        )
