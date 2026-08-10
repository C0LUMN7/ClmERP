# -*- coding: utf-8 -*-
import time

import pytest

from common.dingRobot import send_dd_msg
from common.semail import BuildEmail
from conf.setting import dd_msg

import os
import warnings

_IN_CI = any(os.getenv(var, '').lower() == 'true' for var in ['CI', 'GITHUB_ACTIONS', 'JENKINS_CI'])


@pytest.fixture(scope="session", autouse=True)
def api_session_context():
    # 禁用HTTPS告警，ResourceWarning
    warnings.simplefilter('ignore', ResourceWarning)
    # 每次测试会话重置内存运行上下文，实现会话级变量隔离；
    # 不再清空根目录 extract.yaml，也不删除历史报告文件
    from api.framework.yaml_loader import reset_run_context
    reset_run_context()


def generate_test_summary(terminalreporter):
    """生成测试结果摘要字符串"""
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    duration = time.time() - getattr(terminalreporter, '_sessionstarttime', time.time())

    summary = f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration}
    """
    print(summary)
    return summary


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """自动收集pytest框架执行的测试结果并打印摘要信息"""
    # collect-only 模式只做用例收集：不打印摘要、不发送通知，避免收集命令产生外部副作用
    if config.option.collectonly:
        return
    summary = generate_test_summary(terminalreporter)
    # CI 中只打印摘要，不发送钉钉/邮件通知
    if _IN_CI:
        return
    if dd_msg:
        send_dd_msg(summary)
    stats = terminalreporter.stats
    passed = stats.get('passed', [])
    failed = stats.get('failed', [])
    error = stats.get('error', [])
    skipped = stats.get('skipped', [])
    BuildEmail().main(passed, failed, error, skipped)
