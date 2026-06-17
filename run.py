import argparse
import shutil
import subprocess
import sys
import os
from conf.setting import REPORT_TYPE, ALLURE_HOST, ALLURE_PORT


def _is_ci() -> bool:
    ci_vars = ['CI', 'GITHUB_ACTIONS', 'JENKINS_CI']
    return any(os.getenv(var, '').lower() == 'true' for var in ci_vars)


def _build_pytest_args(suite: str) -> list[str]:
    args = ['-s', '-v']
    if suite == 'all':
        args.append('./testcase/ERP/')
    else:
        args.extend(['-m', suite, './testcase/ERP/'])
    args.extend([
        '--alluredir=./report/temp',
        '--clean-alluredir',
        '--junitxml=./report/results.xml',
    ])
    return args


def _generate_allure_report() -> None:
    cmd = 'allure generate ./report/temp -o ./report/allureReport --clean'
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print('错误: Allure 命令执行失败，请确认 Allure 已正确安装并已添加到 PATH 环境变量')
        print('下载地址: https://github.com/allure-framework/allure2/releases')
        sys.exit(1)


def run_suite(suite: str) -> None:
    if REPORT_TYPE != 'allure':
        print('当前 REPORT_TYPE 不是 allure，跳过测试执行')
        sys.exit(0)

    pytest_args = _build_pytest_args(suite)
    print(f'执行 pytest 参数: {" ".join(pytest_args)}')
    exit_code = pytest.main(pytest_args)

    env_xml = './conf/environment.xml'
    if os.path.exists(env_xml):
        shutil.copy(env_xml, './report/temp')

    _generate_allure_report()

    if not _is_ci():
        subprocess.Popen(
            f'allure open ./report/allureReport --host {ALLURE_HOST} --port {ALLURE_PORT}',
            shell=True,
        )

    sys.exit(exit_code)


if __name__ == '__main__':
    import pytest

    parser = argparse.ArgumentParser(description='ERP 接口自动化测试一键回归入口')
    parser.add_argument(
        '--suite',
        choices=['smoke', 'single', 'business', 'all'],
        default='all',
        help='回归范围: smoke(冒烟) / single(单接口) / business(业务链路) / all(全量)',
    )
    args = parser.parse_args()
    run_suite(args.suite)