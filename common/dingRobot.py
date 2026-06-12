import urllib.parse
import requests
import time
import hmac
import hashlib
import base64
from conf.operationConfig import OperationConfig


def _get_dingtalk_config():
    conf = OperationConfig()
    webhook = conf.get_section_for_data('DINGTALK', 'webhook')
    secret = conf.get_section_for_data('DINGTALK', 'secret')
    return webhook, secret


def generate_sign(secret):
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    str_to_sign = '{}\n{}'.format(timestamp, secret)
    str_to_sign_enc = str_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, str_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def send_dd_msg(content_str, at_all=True):
    webhook, secret = _get_dingtalk_config()
    timestamp, sign = generate_sign(secret)
    url = f'{webhook}&timestamp={timestamp}&sign={sign}'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "msgtype": "text",
        "text": {
            "content": content_str
        },
        "at": {
            "isAtAll": at_all
        },
    }
    res = requests.post(url, json=data, headers=headers)
    return res.text
