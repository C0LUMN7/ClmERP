# -*- coding: utf-8 -*-
import pytest

from shared.notification import generate_test_summary

import warnings


@pytest.fixture(scope="session", autouse=True)
def api_session_context():
    # 禁用HTTPS告警，ResourceWarning
    warnings.simplefilter('ignore', ResourceWarning)
    # 每次测试会话重置内存运行上下文，实现会话级变量隔离；
    # 不再清空根目录 extract.yaml，也不删除历史报告文件
    from api.framework.yaml_loader import reset_run_context
    reset_run_context()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """自动收集 pytest 执行结果并打印摘要信息，不发送外部通知。"""
    # collect-only 模式只做用例收集：不打印摘要、不发送通知，避免收集命令产生外部副作用
    if config.option.collectonly:
        return
    generate_test_summary(terminalreporter)
