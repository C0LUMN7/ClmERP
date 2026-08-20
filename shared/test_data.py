# -*- coding: utf-8 -*-
"""测试数据编号生成器。"""


def generate_module_id():
    """生成测试模块编号，保持 Allure 展示顺序与 pytest 执行顺序一致。"""
    for i in range(1, 1000):
        module_id = 'M' + str(i).zfill(2) + '_'
        yield module_id


def generate_testcase_id():
    """生成测试用例编号。"""
    for i in range(1, 10000):
        case_id = 'C' + str(i).zfill(2) + '_'
        yield case_id


m_id = generate_module_id()
c_id = generate_testcase_id()
