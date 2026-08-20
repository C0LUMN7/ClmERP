# -*- coding: utf-8 -*-
"""轻量 ERP API Client

仅封装跨层用例需要的登录、单据查询和审核状态变更能力。登录接口按
jshERP 现有要求使用密码 MD5 与验证码，不扩展新的安全机制。
"""
import time

import requests
import urllib3

from shared.debugtalk import DebugTalk
from config.settings import ERP_PASSWORD, ERP_USERNAME, get_api_url


class ErpApiClient:
    """ERP 接口客户端：跨层用例用于查询和状态校验。"""

    def __init__(self):
        self.base_url = get_api_url()
        self.session = requests.Session()
        self.token = ""

    def login(self):
        if not self.base_url:
            raise RuntimeError("ERP API 地址未配置")
        if not ERP_USERNAME or not ERP_PASSWORD:
            raise RuntimeError("ERP 登录账号或密码未配置")

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
            response = self.session.post(
                self.base_url + "/user/login",
                json=payload,
                headers={"Content-Type": "application/json;charset=UTF-8"},
                verify=False,
                timeout=15,
            )
            data = response.json()
            token = data.get("data", {}).get("token")
            if response.status_code == 200 and token:
                self.token = token
                return self
            time.sleep(1)
        raise RuntimeError("ERP API 登录失败，已重试 5 次")

    def get_depot_head_detail(self, number: str) -> dict:
        return self._request(
            "GET",
            "/depotHead/getDetailByNumber",
            params={"number": number},
        ).get("data") or {}

    def set_depot_head_status(self, ids, status: str) -> dict:
        return self._request(
            "POST",
            "/depotHead/batchSetStatus",
            json={"ids": str(ids), "status": str(status)},
        )

    def _request(self, method: str, path: str, **kwargs) -> dict:
        if not self.token:
            self.login()
        headers = kwargs.pop("headers", {})
        headers.setdefault("Content-Type", "application/json;charset=UTF-8")
        headers["X-Access-Token"] = self.token
        response = self.session.request(
            method,
            self.base_url + path,
            headers=headers,
            verify=False,
            timeout=15,
            **kwargs,
        )
        if response.text.strip() == "loginOut":
            self.login()
            headers["X-Access-Token"] = self.token
            response = self.session.request(
                method,
                self.base_url + path,
                headers=headers,
                verify=False,
                timeout=15,
                **kwargs,
            )
        response.raise_for_status()
        data = response.json()
        if data.get("code") != 200:
            raise RuntimeError(f"ERP API 请求失败: {path}, 响应: {data}")
        return data
