# -*- coding: utf-8 -*-
"""统一配置读取（最小多环境：cloud_test / local）

- 环境选择：ERP_ENV=cloud_test|local，默认 cloud_test
- 敏感凭据一律通过环境变量或本地未提交配置注入，本文件不写入真实账号密码
- 提供基础 preflight 环境预检：对已配置项给出明确结果，缺失项标记待配置，不伪造通过
"""
import os

ENV = os.getenv('ERP_ENV', 'cloud_test')

# 被测系统信息（明确被测系统为开源项目 jshERP）
SYSTEM = {
    'name': 'jshERP',
    'repository': 'https://github.com/jishenghua/jshERP',
    'environment': ENV,
    'deployed_version': os.getenv('ERP_VERSION', '待确认'),
    # 'deployed_commit': '待确认',  # 可选，能够确认云端实例对应 Commit 时再填写
}

# ERP API / UI 地址与登录凭据（环境变量注入）
ERP_API_URL = os.getenv('ERP_API_URL', '')
ERP_UI_URL = os.getenv('ERP_UI_URL', '')
ERP_USERNAME = os.getenv('ERP_USERNAME', '')
ERP_PASSWORD = os.getenv('ERP_PASSWORD', '')

# MySQL 配置（环境变量注入）
MYSQL_HOST = os.getenv('MYSQL_HOST', '')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME', '')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', '')

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
BUSINESS_IDS = {
    key: os.getenv(_BUSINESS_ID_ENV_VARS[key], default)
    for key, default in _BUSINESS_ID_DEFAULTS.items()
}


def get_api_url():
    """ERP API 地址：优先环境变量 ERP_API_URL，缺失时兼容本地 conf/config.ini

    统一 API 框架的地址读取入口，避免各执行器各自硬编码或重复读取配置。
    """
    if ERP_API_URL:
        return ERP_API_URL.rstrip('/')
    from conf.operationConfig import OperationConfig
    return OperationConfig().get_section_for_data('api_envi', 'host').rstrip('/')


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

    missing_ids = [k for k, v in BUSINESS_IDS.items() if not v]
    print('  [已配置] 核心业务 ID: '
          + ', '.join(f'{k}={v}' for k, v in BUSINESS_IDS.items())
          + (f'（缺失: {", ".join(missing_ids)}）' if missing_ids else ''))
    all_ok = all_ok and not missing_ids
    used_defaults = [k for k in BUSINESS_IDS if not os.getenv(_BUSINESS_ID_ENV_VARS[k])]
    if used_defaults:
        print(f'  提示: {", ".join(used_defaults)} 使用 cloud_test 默认示例值，可通过对应 ERP_* 环境变量覆盖')

    print('结论: ' + ('预检通过' if all_ok else '存在待配置项，连接真实环境前请先补齐'))
    return all_ok
