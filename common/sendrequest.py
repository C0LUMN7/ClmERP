import json
import allure
import pytest
import requests
import urllib3
import time

from conf import setting
from common.recordlog import logs
from requests import utils
from common.readyaml import ReadYamlData
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class SendRequest:
    """发送接口请求，暂时只写了get和post方法的请求"""

    def __init__(self, cookie=None):
        self.cookie = cookie
        self.read = ReadYamlData()

    def get(self, url, data, header):
        """
        :param url: 接口地址
        :param data: 请求参数
        :param header: 请求头
        :return:
        """
        requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            if data is None:
                response = requests.get(url, headers=header, cookies=self.cookie, verify=False)
            else:
                response = requests.get(url, data, headers=header, cookies=self.cookie, verify=False)
        except requests.RequestException as e:
            logs.error(e)
            return None
        except Exception as e:
            logs.error(e)
            return None
        # 响应时间/毫秒
        res_ms = response.elapsed.microseconds / 1000
        # 响应时间/秒
        res_second = response.elapsed.total_seconds()
        response_dict = dict()

        # 接口响应状态码
        response_dict['code'] = response.status_code
        # 接口响应文本
        response_dict['text'] = response.text
        try:
            response_dict['body'] = response.json().get('body')
        except Exception:
            response_dict['body'] = ''
        response_dict['res_ms'] = res_ms
        response_dict['res_second'] = res_second
        return response_dict

    def post(self, url, data, header):
        """
        :param url:
        :param data: verify=False忽略SSL证书验证
        :param header:
        :return:
        """
        # 控制台输出InsecureRequestWarning错误
        requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            if data is None:
                response = requests.post(url, header, cookies=self.cookie, verify=False)
            else:
                response = requests.post(url, data, headers=header, cookies=self.cookie, verify=False)
        except requests.RequestException as e:
            logs.error(e)
            return None
        except Exception as e:
            logs.error(e)
            return None
        # 响应时间/毫秒
        res_ms = response.elapsed.microseconds / 1000
        # 响应时间/秒
        res_second = response.elapsed.total_seconds()
        response_dict = dict()
        # 接口响应状态码
        response_dict['code'] = response.status_code
        # 接口响应文本
        response_dict['text'] = response.text
        try:
            response_dict['body'] = response.json().get('body')
        except Exception:
            response_dict['body'] = ''
        response_dict['res_ms'] = res_ms
        response_dict['res_second'] = res_second
        return response_dict

    def _relogin(self):
        """重新登录获取新token"""
        from conf.operationConfig import OperationConfig
        from common.debugtalk import DebugTalk
        host = OperationConfig().get_section_for_data('api_envi', 'host')
        dt = DebugTalk()
        for attempt in range(5):
            DebugTalk._captcha_data = None
            time.sleep(1)
            try:
                payload = {
                    'loginName': 'jsh',
                    'password': dt.md5_encryption('123456'),
                    'code': dt.get_captcha_code(),
                    'uuid': dt.get_captcha_uuid()
                }
                headers = {'Content-Type': 'application/json;charset=UTF-8'}
                r = requests.post(host + '/user/login', json=payload, headers=headers, verify=False, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    new_token = data.get('data', {}).get('token')
                    if new_token:
                        self.read.write_yaml_data({'token': new_token})
                        logs.info(f'[send_request] 重新登录成功，新token: {new_token}')
                        return new_token
            except Exception as e:
                logs.warning(f'[send_request] 登录异常 (第{attempt+1}次): {e}')
        return None

    def send_request(self, **kwargs):

        session = requests.session()
        result = None
        cookie = {}
        try:
            result = session.request(**kwargs)
            set_cookie = requests.utils.dict_from_cookiejar(result.cookies)
            if set_cookie:
                cookie['Cookie'] = set_cookie
                self.read.write_yaml_data(cookie)
                logs.info("cookie：%s" % cookie)
            logs.info("接口返回信息：%s" % result.text if result.text else result)

            # 自动重新登录：检测到loginOut时循环重试（最多3次）
            max_relogin_retries = 3
            for rl_attempt in range(max_relogin_retries):
                if result and result.text and result.text.strip() == 'loginOut':
                    logs.warning(f'[send_request] 检测到loginOut，正在重新登录并重试 (第{rl_attempt+1}次)...')
                    new_token = self._relogin()
                    if new_token:
                        if 'headers' in kwargs:
                            kwargs['headers']['X-Access-Token'] = new_token
                        result = session.request(**kwargs)
                        logs.info("接口返回信息(重试)：%s" % result.text if result.text else result)
                    else:
                        break
                else:
                    break

        except requests.exceptions.ConnectionError:
            logs.error("ConnectionError--连接异常")
            pytest.fail("接口请求异常，可能是request的连接数过多或请求速度过快导致程序报错！")
        except requests.exceptions.HTTPError:
            logs.error("HTTPError--http异常")
        except requests.exceptions.RequestException as e:
            logs.error(e)
            pytest.fail("请求异常，请检查系统或数据是否正常！")
        return result

    def run_main(self, name, url, case_name, header, method, cookies=None, file=None, **kwargs):
        """
        接口请求
        :param name: 接口名
        :param url: 接口地址
        :param case_name: 测试用例
        :param header:请求头
        :param method:请求方法
        :param cookies：默认为空
        :param file: 上传文件接口
        :param kwargs: 请求参数，根据yaml文件的参数类型
        :return:
        """

        try:
            # 收集报告日志
            logs.info('接口名称：%s' % name)
            logs.info('请求地址：%s' % url)
            logs.info('请求方式：%s' % method)
            logs.info('测试用例名称：%s' % case_name)
            logs.info('请求头：%s' % header)
            logs.info('Cookie：%s' % cookies)
            req_params = json.dumps(kwargs, ensure_ascii=False)
            if "data" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
            elif "json" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
            elif "params" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
        except Exception as e:
            logs.error(e)
        # time.sleep(0.5)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        response = self.send_request(method=method,
                                     url=url,
                                     headers=header,
                                     cookies=cookies,
                                     files=file,
                                     timeout=setting.API_TIMEOUT,
                                     verify=False,
                                     **kwargs)
        return response
