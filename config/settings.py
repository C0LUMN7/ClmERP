# -*- coding: utf-8 -*-
"""统一配置读取（最小多环境：cloud_test / local）

- 环境选择：ERP_ENV 或 config/local.ini [system] environment，默认 cloud_test
- 敏感凭据优先通过环境变量注入；缺失时读取本地未提交的 config/local.ini
- 提供基础 preflight 环境预检：对已配置项给出明确结果，缺失项标记待配置，不伪造通过
"""
import configparser
import logging
import os
from pathlib import Path

_LOCAL_CONFIG = None
_CONFIG_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _CONFIG_DIR.parent
_LOCAL_CONFIG_PATH = _CONFIG_DIR / 'local.ini'
# 仅作为历史本地配置兜底，不属于当前仓库展示结构；保留读取避免影响已有本地环境。
_LEGACY_CONFIG_PATH = _REPO_ROOT / 'conf' / 'config.ini'

# 日志、报告与接口超时配置
LOG_LEVEL = logging.DEBUG
STREAM_LOG_LEVEL = logging.DEBUG
LOG_DIR = _REPO_ROOT / 'reports' / 'logs'
API_TIMEOUT = 60
REPORT_TYPE = 'allure'
ALLURE_HOST = '127.0.0.1'
ALLURE_PORT = 0


def _local_config():
    """读取本地 config/local.ini；历史 conf/config.ini 仅作本地兜底。"""
    global _LOCAL_CONFIG
    if _LOCAL_CONFIG is None:
        parser = configparser.ConfigParser()
        parser.read([_LEGACY_CONFIG_PATH, _LOCAL_CONFIG_PATH], encoding='utf-8')
        _LOCAL_CONFIG = parser
    return _LOCAL_CONFIG


def _config_value(section, option, default=''):
    parser = _local_config()
    if parser.has_option(section, option):
        return parser.get(section, option)
    return default


def _env_or_config(env_name, section, option, default=''):
    return os.getenv(env_name) or _config_value(section, option, default)


def _has_env_or_config(env_name, section, option):
    return bool(os.getenv(env_name) or _config_value(section, option, ''))


ENV = _env_or_config('ERP_ENV', 'system', 'environment', 'cloud_test')

# 被测系统信息（明确被测系统为开源项目 jshERP）
SYSTEM = {
    'name': 'jshERP',
    'repository': 'https://github.com/jishenghua/jshERP',
    'environment': ENV,
    'deployed_version': _env_or_config('ERP_VERSION', 'system', 'deployed_version', '待确认'),
    # 'deployed_commit': '待确认',  # 可选，能够确认云端实例对应 Commit 时再填写
}

# ERP API / UI 地址与登录凭据（环境变量优先，本地 config/local.ini 兜底）
ERP_API_URL = _env_or_config('ERP_API_URL', 'api_envi', 'host', '')
ERP_UI_URL = _env_or_config('ERP_UI_URL', 'api_envi', 'ui_host', '')
ERP_USERNAME = _env_or_config('ERP_USERNAME', 'LOGIN', 'username', '')
ERP_PASSWORD = _env_or_config('ERP_PASSWORD', 'LOGIN', 'password', '')

# ERP UI 登录成功判断条件（必须来自真实 jshERP 页面资料，支持 url/title/text）
# 资料缺失时保持为空，UI 冒烟用例会在启动浏览器前跳过并说明原因
UI_LOGIN_SUCCESS_KIND = _env_or_config('ERP_UI_LOGIN_SUCCESS_KIND', 'UI', 'login_success_kind', '')
UI_LOGIN_SUCCESS_VALUE = _env_or_config('ERP_UI_LOGIN_SUCCESS_VALUE', 'UI', 'login_success_value', '')

# MySQL 配置（环境变量优先，本地 config/local.ini 兜底）
MYSQL_HOST = _env_or_config('MYSQL_HOST', 'MYSQL', 'host', '')
MYSQL_PORT = _env_or_config('MYSQL_PORT', 'MYSQL', 'port', '3306')
MYSQL_USERNAME = _env_or_config('MYSQL_USERNAME', 'MYSQL', 'username', '')
MYSQL_PASSWORD = _env_or_config('MYSQL_PASSWORD', 'MYSQL', 'password', '')
MYSQL_DATABASE = _env_or_config('MYSQL_DATABASE', 'MYSQL', 'database', '')

# 显式通知配置（环境变量优先，本地 config/local.ini 兜底）
DINGTALK_WEBHOOK = _env_or_config('DINGTALK_WEBHOOK', 'DINGTALK', 'webhook', '')
DINGTALK_SECRET = _env_or_config('DINGTALK_SECRET', 'DINGTALK', 'secret', '')
EMAIL_HOST = _env_or_config('EMAIL_HOST', 'EMAIL', 'host', '')
EMAIL_USER = _env_or_config('EMAIL_USER', 'EMAIL', 'user', '')
EMAIL_PASSWORD = _env_or_config('EMAIL_PASSWORD', 'EMAIL', 'passwd', '')
EMAIL_ADDRESSEE = _env_or_config('EMAIL_ADDRESSEE', 'EMAIL', 'addressee', '')
EMAIL_SUBJECT = _env_or_config('EMAIL_SUBJECT', 'EMAIL', 'subject', 'ERP 自动化测试结果')

# 核心业务 ID（商品分类/仓库/供应商/客户/结算账户/财务账户）
# 优先通过环境变量注入；未设置时使用当前 cloud_test 环境的默认示例值，
# 切换环境或业务 ID 失效时需重新确认映射，不要再写回 YAML 用例。
_BUSINESS_ID_DEFAULTS = {
    'category_id': '91',
    'depot_id': '124',
    'supplier_organ_id': '196',
    'customer_organ_id': '204',
    'settle_account_id': '86',
    'finance_account_id': '105',
}
_BUSINESS_ID_ENV_VARS = {
    'category_id': 'ERP_CATEGORY_ID',
    'depot_id': 'ERP_DEPOT_ID',
    'supplier_organ_id': 'ERP_SUPPLIER_ORGAN_ID',
    'customer_organ_id': 'ERP_CUSTOMER_ORGAN_ID',
    'settle_account_id': 'ERP_SETTLE_ACCOUNT_ID',
    'finance_account_id': 'ERP_FINANCE_ACCOUNT_ID',
}
BUSINESS_IDS = {}
for key, default in _BUSINESS_ID_DEFAULTS.items():
    BUSINESS_IDS[key] = _env_or_config(_BUSINESS_ID_ENV_VARS[key], 'BUSINESS_IDS', key, default)


def get_api_url():
    """ERP API 地址：优先环境变量 ERP_API_URL，缺失时读取本地配置兜底。

    统一 API 框架的地址读取入口，避免各执行器各自硬编码或重复读取配置。
    """
    if ERP_API_URL:
        return ERP_API_URL.rstrip('/')
    return ''


def preflight():
    """基础环境预检：只检查当前执行真正依赖的配置项。

    缺失项输出“待配置”，不伪造通过结果；全部就绪才返回 True。
    """
    print(f'被测系统: {SYSTEM["name"]}（{SYSTEM["repository"]}）')
    print(f'环境: {SYSTEM["environment"]}，部署版本: {SYSTEM["deployed_version"]}')
    print('--- 环境预检 ---')

    checks = [
        ('ERP API 地址', bool(ERP_API_URL)),
        ('ERP UI 地址', bool(ERP_UI_URL)),
        ('测试账号', bool(ERP_USERNAME and ERP_PASSWORD)),
        ('MySQL 配置', bool(MYSQL_HOST and MYSQL_PORT and MYSQL_USERNAME and MYSQL_PASSWORD and MYSQL_DATABASE)),
    ]
    all_ok = True
    for name, ok in checks:
        print(f'  [{"已配置" if ok else "待配置"}] {name}')
        all_ok = all_ok and ok

    ui_login_judge_ready = bool(UI_LOGIN_SUCCESS_KIND and UI_LOGIN_SUCCESS_VALUE)
    print(f'  [{"已配置" if ui_login_judge_ready else "待确认"}] UI 登录成功判断条件'
          + ('' if ui_login_judge_ready else '（需人工提供真实 jshERP 页面资料；缺失时 UI 冒烟将跳过）'))

    missing_ids = [k for k, v in BUSINESS_IDS.items() if not v]
    print('  [已配置] 核心业务 ID: '
          + ', '.join(f'{k}={v}' for k, v in BUSINESS_IDS.items())
          + (f'（缺失: {", ".join(missing_ids)}）' if missing_ids else ''))
    all_ok = all_ok and not missing_ids
    used_defaults = [
        k for k in BUSINESS_IDS
        if not _has_env_or_config(_BUSINESS_ID_ENV_VARS[k], 'BUSINESS_IDS', k)
    ]
    if used_defaults:
        print(f'  提示: {", ".join(used_defaults)} 使用 cloud_test 默认示例值，可通过对应 ERP_* 环境变量覆盖')

    print('结论: ' + ('预检通过' if all_ok else '存在待配置项，连接真实环境前请先补齐'))
    return all_ok
