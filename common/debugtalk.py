import base64
import calendar
import datetime
import hashlib
import os.path
import random
import re
import time
from hashlib import sha1
from conf.setting import DIR_BASE
from pandas.tseries.offsets import Day
from common.readyaml import ReadYamlData
import csv


class DebugTalk:
    _captcha_data = None

    def __init__(self):
        self.read = ReadYamlData()

    def get_extract_data(self, node_name, randoms=None) -> str:
        """
        获取提取变量：优先读取当前测试会话运行上下文（内存），缺失时兼容旧 extract.yaml
        :param node_name: 变量名
        :param randoms: int类型，0：随机读取；-1：读取全部，返回字符串形式；-2：读取全部，返回列表形式；其他根据列表索引取值，取第一个值为1，第二个为2，以此类推;
        :return:
        """
        from api.framework.yaml_loader import get_run_context
        context = get_run_context()
        if node_name in context:
            return self._pick_context_value(context.get(node_name), randoms)
        data = self.read.get_extract_yaml(node_name)
        if data is None:
            raise KeyError(f'运行上下文缺少变量 {node_name}（变量来源：当前会话接口提取结果或旧 extract.yaml）')
        if randoms is not None and bool(re.compile(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$').match(randoms)):
            randoms = int(randoms)
            data_value = {
                randoms: self.get_extract_order_data(data, randoms),
                0: random.choice(data),
                -1: ','.join(data),
                -2: ','.join(data).split(','),
            }
            data = data_value[randoms]
        else:
            data = self.read.get_extract_yaml(node_name, randoms)
        return data

    @staticmethod
    def _pick_context_value(value, randoms):
        """从运行上下文取值；randoms 仅对列表值生效，语义与旧 extract.yaml 一致"""
        if randoms is None or not isinstance(value, list):
            return value
        if not re.match(r'^[-+]?[0-9]+$', randoms):
            return value
        index = int(randoms)
        if index == 0:
            return random.choice(value)
        if index == -1:
            return ','.join(str(v) for v in value)
        if index == -2:
            return value
        return value[index - 1]

    def get_extract_order_data(self, data, randoms):
        """获取extract.yaml数据，不为0、-1、-2，则按顺序读取文件key的数据"""
        if randoms not in [0, -1, -2]:
            return data[randoms - 1]

    def _get_host(self):
        from config.settings import get_api_url
        return get_api_url()

    def _get_captcha(self):
        if DebugTalk._captcha_data is None:
            import io
            import json
            import urllib.request
            import warnings
            import ddddocr
            from PIL import Image, ImageOps, ImageFilter
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                ocr = ddddocr.DdddOcr(beta=False)
                for attempt in range(5):
                    req = urllib.request.Request(self._get_host() + '/user/randomImage')
                    resp = urllib.request.urlopen(req)
                    data = json.loads(resp.read())
                    b64 = data['data']['base64'].split(',')[1]
                    uuid = data['data']['uuid']
                    img_bytes = base64.b64decode(b64)
                    pil = Image.open(io.BytesIO(img_bytes)).convert('L')
                    pil = ImageOps.autocontrast(pil, cutoff=5)
                    pil = pil.filter(ImageFilter.SHARPEN)
                    pil = pil.point(lambda x: 0 if x < 128 else 255, '1')
                    buf = io.BytesIO()
                    pil.save(buf, format='PNG')
                    processed = buf.getvalue()
                    code = ocr.classification(processed)
                    if len(code) == 4:
                        DebugTalk._captcha_data = {'uuid': uuid, 'code': code}
                        break
        return DebugTalk._captcha_data

    def get_captcha_code(self):
        return self._get_captcha()['code']

    def get_captcha_uuid(self):
        return self._get_captcha()['uuid']

    def get_login_name(self):
        """登录账号：从环境变量 ERP_USERNAME 读取，避免写入 YAML"""
        from config.settings import ERP_USERNAME
        if not ERP_USERNAME:
            raise RuntimeError('登录账号未配置：请通过环境变量 ERP_USERNAME 提供测试账号，不要写入代码或 YAML')
        return ERP_USERNAME

    def get_login_password(self):
        """登录密码的 MD5：从环境变量 ERP_PASSWORD 读取，避免写入 YAML"""
        from config.settings import ERP_PASSWORD
        if not ERP_PASSWORD:
            raise RuntimeError('登录密码未配置：请通过环境变量 ERP_PASSWORD 提供测试密码，不要写入代码或 YAML')
        return self.md5_encryption(ERP_PASSWORD)

    def get_business_id(self, key):
        """读取配置的核心业务 ID（分类/仓库/供应商/客户/账户），避免散落在 YAML

        值来自 config/settings.py（环境变量优先，缺省为 cloud_test 默认示例）；
        数字值保持 int 类型，保证与原有 YAML 请求体语义一致。
        """
        from config.settings import BUSINESS_IDS
        value = BUSINESS_IDS.get(key)
        if not value:
            raise RuntimeError(f'核心业务 ID 未配置: {key}，请通过 ERP_* 环境变量或 config/settings.py 配置')
        if str(value).isdigit():
            return int(value)
        return value

    def get_material_id_by_name(self, name_prefix):
        """按本次创建的唯一商品名前缀精确查询商品 ID（数据库）

        商品名 = 前缀 + 会话固定运行 ID；只匹配本次创建的商品，
        避免更新/删除操作作用于环境中原有商品。
        """
        from common.connection import ConnectMysql
        name = f'{name_prefix}{self.fixed_timestamp()}'
        rows = ConnectMysql().query_all(
            f"SELECT id FROM jsh_material WHERE name = '{name}' AND delete_flag = '0'")
        if not rows:
            raise RuntimeError(f'数据库未找到本次创建的商品: {name}，请确认创建步骤已执行且名称唯一')
        return rows[0][0]

    def get_depot_id_by_name(self, name_prefix):
        """按本次创建的唯一仓库名前缀精确查询仓库 ID（数据库）

        仓库名 = 前缀 + 会话固定运行 ID；只匹配本次创建的仓库，
        更新、删除前必须使用本函数确认精确 ID，避免作用于真实仓库。
        """
        from common.connection import ConnectMysql
        name = f'{name_prefix}{self.fixed_timestamp()}'
        rows = ConnectMysql().query_all(
            f"SELECT id FROM jsh_depot WHERE name = '{name}' AND delete_flag = '0'")
        if not rows:
            raise RuntimeError(f'数据库未找到本次创建的仓库: {name}，请确认创建步骤已执行且名称唯一')
        return rows[0][0]

    def md5_encryption(self, params):
        """参数MD5加密"""
        enc_data = hashlib.md5()
        enc_data.update(params.encode(encoding="utf-8"))
        return enc_data.hexdigest()

    def sha1_encryption(self, params):
        """参数sha1加密"""
        enc_data = sha1()
        enc_data.update(params.encode(encoding="utf-8"))
        return enc_data.hexdigest()

    def base64_encryption(self, params):
        """base64加密"""
        base_params = params.encode("utf-8")
        encr = base64.b64encode(base_params)
        return encr

    def timestamp(self):
        """获取当前时间戳，10位"""
        t = int(time.time())
        return t

    def timestamp_thirteen(self):
        """获取当前的时间戳，13位"""
        t = int(time.time()) * 1000
        return t

    def start_time(self):
        """获取当前时间的前一天标准时间"""
        now_time = datetime.datetime.now()
        day_before_time = (now_time - 1 * Day()).strftime("%Y-%m-%d %H:%M:%S")
        return day_before_time

    def end_time(self):
        """获取当前时间标准时间格式"""
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return now_time

    def start_forward_time(self):
        """获取当前时间的前15天标准时间，年月日"""
        now_time = datetime.datetime.now()
        day_before_time = (now_time - 15 * Day()).strftime("%Y-%m-%d")
        return day_before_time

    def start_after_time(self):
        """获取当前时间的后7天标准时间，年月日"""
        now_time = datetime.datetime.now()
        day_after_time = (now_time + 7 * Day()).strftime("%Y-%m-%d")
        return day_after_time

    def end_year_time(self):
        """获取当前时间标准时间格式，年月日"""
        now_time = datetime.datetime.now().strftime("%Y-%m-%d")
        return now_time

    def today_zero_tenstamp(self):
        """获取当天00:00:00时间戳，10位时间戳"""
        time_stamp = int(time.mktime(datetime.date.today().timetuple()))
        return time_stamp

    def today_zero_stamp(self):
        """获取当天00:00:00时间戳，13位时间戳"""
        time_stamp = int(time.mktime(datetime.date.today().timetuple())) * 1000
        return time_stamp

    def specified_zero_tamp(self, days):
        """获取当前日期指定日期的00:00:00时间戳，days：往前为负数，往后为整数"""
        tom = datetime.date.today() + datetime.timedelta(days=int(days))
        date_tamp = int(time.mktime(time.strptime(str(tom), '%Y-%m-%d'))) * 1000
        return date_tamp

    def specified_end_tamp(self, days):
        """获取当前日期指定日期的23:59:59时间戳，days：往前为负数，往后为整数"""
        tom = datetime.date.today() + datetime.timedelta(days=int(days) + 1)
        date_tamp = int(time.mktime(time.strptime(str(tom), '%Y-%m-%d'))) - 1
        return date_tamp * 1000

    def today_end_stamp(self):
        """获取当天23:59:59时间戳"""
        # 今天日期
        today = datetime.date.today()
        # 明天日期
        tomorrow = today + datetime.timedelta(days=1)
        today_end_time = int(time.mktime(time.strptime(str(tomorrow), '%Y-%m-%d'))) - 1
        return today_end_time * 1000

    def month_start_time(self):
        """获取本月第一天标准时间，年月日"""
        # 今天日期
        now = datetime.datetime.now()
        this_month_start = datetime.datetime(now.year, now.month, 1).strftime("%Y-%m-%d")
        return this_month_start

    def month_end_time(self):
        """获取本月最后一天标准时间，年月日"""
        # 今天日期
        now = datetime.datetime.now()
        this_month_end = datetime.datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1]).strftime(
            "%Y-%m-%d")
        return this_month_end

    def month_first_time(self):
        """本月1号00:00:00时间戳，13位"""
        # 今天日期
        now = datetime.datetime.now()
        # 本月第一天日期
        this_month_start = datetime.datetime(now.year, now.month, 1)
        first_time_stamp = int(time.mktime(this_month_start.timetuple())) * 1000
        return first_time_stamp

    def fenceAlarm_alarmType_random(self):
        alarm_type = ["1", "3", "8", "2", "5", "6"]
        fence_alarm = random.choice(alarm_type)
        return fence_alarm

    def fatigueAlarm_alarmType_random(self):
        alarm_type = ["1", "3", "8"]
        fatigue_alarm = random.choice(alarm_type)
        return fatigue_alarm

    def jurisdictionAlarm_random(self):
        alarm_type = ["1", "3", "8", "2", "5", "6", "9"]
        jurisdiction_alarm = random.choice(alarm_type)
        return jurisdiction_alarm

    def read_csv_data(self, file_name, index):
        """读取csv数据，csv文件中不用带字段名，直接写测试数据即可"""
        with open(os.path.join(DIR_BASE, 'data', file_name), 'r', encoding='utf-8') as f:
            csv_reader = list(csv.reader(f))
            user_lst, passwd_lst = [], []
            for user, passwd in csv_reader:
                user_lst.append(user)
                passwd_lst.append(passwd)
            return user_lst[0], passwd_lst[0]

    def get_baseurl(self, host):
        from conf.operationConfig import OperationConfig
        conf = OperationConfig()
        url = conf.get_section_for_data('api_envi', host)
        return url

    _fixed_ts = None

    def fixed_timestamp(self):
        """获取缓存的13位时间戳，在同一测试会话中始终返回相同值"""
        if DebugTalk._fixed_ts is None:
            DebugTalk._fixed_ts = str(int(time.time() * 1000))
        return DebugTalk._fixed_ts

    def gen_bar_code(self):
        """生成唯一条码并写入运行上下文，供后续 depotHead 使用

        Token 优先从运行上下文读取，缺失时兼容旧 extract.yaml；不再写根目录 extract.yaml。
        """
        import requests as req
        from api.framework.yaml_loader import get_run_context
        from config.settings import get_api_url
        context = get_run_context()
        host = get_api_url()
        token = context.get('token') if 'token' in context else self.read.get_extract_yaml('token')
        headers = {"X-Access-Token": token, "Content-Type": "application/json;charset=UTF-8"}
        r = req.get(host + '/material/getMaxBarCode', headers=headers)
        max_bc = r.json()['data']['barCode']
        bc = str(int(max_bc) + 1)
        context.set('barCode', bc)
        return bc
