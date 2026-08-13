import argparse
import shutil
import subprocess
import sys
import os
import time
from conf.setting import REPORT_TYPE, ALLURE_HOST, ALLURE_PORT


def _is_ci() -> bool:
    ci_vars = ['CI', 'GITHUB_ACTIONS', 'JENKINS_CI']
    return any(os.getenv(var, '').lower() == 'true' for var in ci_vars)


# suite 到 pytest marker 的映射；negative 为异常场景的标准套件名，
# exception 保留作为旧命令别名（现有用例标记统一使用 negative）
SUITE_MARKERS = {
    'smoke': 'smoke',
    'single': 'single',
    'business': 'business',
    'negative': 'negative',
    'exception': 'negative',
}


def _build_pytest_args(test_type: str, suite: str, browser: str = '', headed: bool = False) -> list[str]:
    """按测试类型构建 pytest 参数：api/ui 使用各自用例目录和 Allure 结果目录。

    ui 额外传入官方 pytest-playwright 参数：浏览器类型、有头模式，
    以及截图/视频/Trace 产物配置（统一收敛到 reports/playwright）。
    """
    if test_type == 'api':
        target = './api/'
        alluredir = './reports/allure-results/api'
    else:
        target = './ui/'
        alluredir = './reports/allure-results/ui'

    args = ['-s', '-v']
    if browser:
        args.append(f'--browser={browser}')
    if headed:
        args.append('--headed')
    if test_type == 'ui':
        # UI 失败截图/视频/Trace 自动留存，产物统一到 reports/playwright
        args.extend([
            '--output=./reports/playwright',
            '--screenshot=only-on-failure',
            '--video=retain-on-failure',
            '--tracing=retain-on-failure',
        ])
    marker = SUITE_MARKERS.get(suite)
    if marker:
        args.extend(['-m', marker, target])
    else:
        args.append(target)
    args.extend([
        f'--alluredir={alluredir}',
        f'--junitxml=./reports/{test_type}_results.xml',
    ])
    return args


def _generate_allure_report(test_type: str) -> str:
    """将指定类型的 Allure 原始结果生成为 HTML 报告，返回报告目录。

    报告生成到带时间戳的唯一子目录（reports/allure-report/<类型>-<时间戳>），
    不覆盖、不清理任何已有报告目录，也不使用 --clean。
    """
    report_dir = f'./reports/allure-report/{test_type}-{time.strftime("%Y%m%d-%H%M%S")}'
    if os.path.exists(report_dir):
        # 同一秒内重复执行时追加进程号，保证目录不冲突
        report_dir = f'{report_dir}-{os.getpid()}'
    cmd = f'allure generate ./reports/allure-results/{test_type} -o {report_dir}'
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print('错误: Allure 命令执行失败，请确认 Allure 已正确安装并已添加到 PATH 环境变量')
        print('下载地址: https://github.com/allure-framework/allure2/releases')
        sys.exit(1)
    return report_dir


def run_suite(test_type: str, suite: str, browser: str = '', headed: bool = False) -> None:
    if REPORT_TYPE != 'allure':
        print('当前 REPORT_TYPE 不是 allure，跳过测试执行')
        sys.exit(0)

    pytest_args = _build_pytest_args(test_type, suite, browser, headed)
    print(f'执行 pytest 参数: {" ".join(pytest_args)}')
    exit_code = pytest.main(pytest_args)

    env_xml = './conf/environment.xml'
    results_dir = f'./reports/allure-results/{test_type}'
    if os.path.exists(env_xml):
        shutil.copy(env_xml, results_dir)

    report_dir = _generate_allure_report(test_type)

    if not _is_ci():
        subprocess.Popen(
            f'allure open {report_dir} --host {ALLURE_HOST} --port {ALLURE_PORT}',
            shell=True,
        )

    sys.exit(exit_code)


if __name__ == '__main__':
    import pytest

    parser = argparse.ArgumentParser(description='ERP 自动化测试统一执行入口')
    parser.add_argument(
        'test_type',
        choices=['api', 'ui', 'preflight'],
        help='测试类型: api(接口) / ui(UI) / preflight(环境预检)',
    )
    parser.add_argument(
        '--suite',
        choices=['smoke', 'single', 'business', 'negative', 'exception', 'all'],
        default='all',
        help='回归范围: smoke(冒烟) / single(单接口) / business(业务链路) / negative(异常场景) / all(全量)；exception 为 negative 的旧命令别名',
    )
    parser.add_argument(
        '--browser',
        choices=['chromium', 'firefox', 'webkit'],
        default=None,
        help='UI 浏览器类型（仅对 ui 有效），默认 chromium，默认 headless',
    )
    parser.add_argument(
        '--headed',
        action='store_true',
        help='UI 有头模式运行（仅对 ui 有效）',
    )
    args = parser.parse_args()

    if args.test_type == 'ui' and args.suite not in ('smoke', 'all'):
        # UI 套件范围保持明确：只收集 ./ui/ 目录，不会误触发 API 回归、数据库清理或性能测试
        parser.error('ui 当前只支持 --suite smoke / all')
    if args.test_type != 'ui' and (args.browser or args.headed):
        parser.error('--browser / --headed 仅对 ui 命令有效')
    if args.test_type == 'preflight':
        from config.settings import preflight
        sys.exit(0 if preflight() else 1)

    run_suite(args.test_type, args.suite, args.browser or '', args.headed)