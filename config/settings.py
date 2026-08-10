# -*- coding: utf-8 -*-
"""P0: 统一配置读取（最小多环境：cloud_test / local）

- 环境选择：ERP_ENV=cloud_test|local，默认 cloud_test
- 敏感凭据一律通过环境变量或本地未提交配置注入，本文件不写入真实账号密码
- 提供基础 preflight 环境预检：对已配置项给出明确结果，缺失项标记待配置，不伪造通过
"""
import os

ENV = os.getenv('ERP_ENV', 'cloud_test')

# 被测系统信息（P0 目标 6：明确被测系统为开源项目 jshERP）
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

# 核心业务 ID 配置占位（商品分类/仓库/供应商/客户/账户，当前环境值待确认）
BUSINESS_IDS = {
    'category_id': os.getenv('ERP_CATEGORY_ID', ''),
    'depot_id': os.getenv('ERP_DEPOT_ID', ''),
    'organ_id': os.getenv('ERP_ORGAN_ID', ''),
    'account_id': os.getenv('ERP_ACCOUNT_ID', ''),
}


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
    print(f'  [{"已配置" if not missing_ids else "待配置"}] 核心业务 ID'
          + (f'（缺失: {", ".join(missing_ids)}）' if missing_ids else ''))
    all_ok = all_ok and not missing_ids

    print('结论: ' + ('预检通过' if all_ok else '存在待配置项，连接真实环境前请先补齐'))
    return all_ok
