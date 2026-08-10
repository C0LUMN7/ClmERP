# -*- coding: utf-8 -*-
"""旧业务场景执行器兼容层

原请求、模板、提取、断言和自动重登实现已统一到 api/framework/runner.py。
本文件保留 RequestBase 类与 specification_yaml() 签名作为兼容薄封装，
内部委托统一 Runner 的 run_scenario() 顺序执行多步骤业务场景。
"""


class RequestBase:
    """多步骤业务场景兼容入口：委托统一 Runner 的 run_scenario()"""

    def specification_yaml(self, case_info):
        """
        兼容薄封装：委托统一 Runner 顺序执行多步骤业务场景
        :param case_info: dict类型，包含 baseInfo 与 testCase 列表
        :return:
        """
        from api.framework.runner import run_scenario
        steps = [(case_info['baseInfo'], tc) for tc in case_info['testCase']]
        run_scenario(steps)
