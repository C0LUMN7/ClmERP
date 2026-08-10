# -*- coding: utf-8 -*-
"""旧单接口执行器兼容层

原请求、模板、提取、断言和自动重登实现已统一到 api/framework/runner.py。
本文件保留 RequestBase 类与 specification_yaml() 签名作为兼容薄封装，
内部委托统一 Runner 的 run_case() 执行，保证 testcase/ 历史用例入口不破坏。
"""


class RequestBase:
    """单接口用例兼容入口：委托统一 Runner 的 run_case()"""

    def specification_yaml(self, base_info, test_case):
        """
        兼容薄封装：委托统一 Runner 执行单条接口用例
        :param base_info: yaml文件里面的baseInfo
        :param test_case: yaml文件里面的testCase
        :return:
        """
        from api.framework.runner import run_case
        run_case(base_info, test_case)
