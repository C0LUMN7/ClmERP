import argparse
import shutil
import subprocess
import sys
import os
from conf.setting import REPORT_TYPE, ALLURE_HOST, ALLURE_PORT


def _is_ci() -> bool:
    ci_vars = ['CI', 'GITHUB_ACTIONS', 'JENKINS_CI']
    return any(os.getenv(var, '').lower() == 'true' for var in ci_vars)


def _build_pytest_args(test_type: str, suite: str) -> list[str]:
    """按测试类型构建 pytest 参数：api/ui 使用各自用例目录和 Allure 结果目录"""
    if test_type == 'api':
        target = './api/'
        alluredir = './reports/allure-results/api'
    else:
        target = './ui/'
        alluredir = './reports/allure-results/ui'

    args = ['-s', '-v']
    if suite == 'all':
        args.append(target)
    else:
        args.extend(['-m', suite, target])
    args.extend([
        f'--alluredir={alluredir}',
        f'--junitxml=./reports/{test_type}_results.xml',
    ])
    return args


def _generate_allure_report(test_type: str) -> None:
    """将指定类型的 Allure 原始结果合并生成为统一 HTML 报告"""
    cmd = f'allure generate ./reports/allure-results/{test_type} -o ./reports/allure-report'
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print('错误: Allure 命令执行失败，请确认 Allure 已正确安装并已添加到 PATH 环境变量')
        print('下载地址: https://github.com/allure-framework/allure2/releases')
        sys.exit(1)


def run_suite(test_type: str, suite: str) -> None:
    if REPORT_TYPE != 'allure':
        print('当前 REPORT_TYPE 不是 allure，跳过测试执行')
        sys.exit(0)

    pytest_args = _build_pytest_args(test_type, suite)
    print(f'执行 pytest 参数: {" ".join(pytest_args)}')
    exit_code = pytest.main(pytest_args)

    env_xml = './conf/environment.xml'
    results_dir = f'./reports/allure-results/{test_type}'
    if os.path.exists(env_xml):
        shutil.copy(env_xml, results_dir)

    _generate_allure_report(test_type)

    if not _is_ci():
        subprocess.Popen(
            f'allure open ./reports/allure-report --host {ALLURE_HOST} --port {ALLURE_PORT}',
            shell=True,
        )

    sys.exit(exit_code)


if __name__ == '__main__':
    import pytest

    parser = argparse.ArgumentParser(description='ERP 自动化测试统一执行入口（P0 合并骨架）')
    parser.add_argument(
        'test_type',
        choices=['api', 'ui', 'preflight'],
        help='测试类型: api(接口) / ui(UI) / preflight(环境预检)',
    )
    parser.add_argument(
        '--suite',
        choices=['smoke', 'single', 'business', 'exception', 'all'],
        default='all',
        help='回归范围: smoke(冒烟) / single(单接口) / business(业务链路) / exception(异常场景) / all(全量)',
    )
    args = parser.parse_args()

    if args.test_type == 'preflight':
        from config.settings import preflight
        sys.exit(0 if preflight() else 1)

    run_suite(args.test_type, args.suite)